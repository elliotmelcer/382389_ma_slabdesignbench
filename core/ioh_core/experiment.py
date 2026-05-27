import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from ioh.iohcpp.logger import trigger as ltr
import ioh
import json

"""
Adapted from: Max Dombrowski

This module provides a function run_experiment():
 1. applies an optimization algorithm to one or more problem bundles
 2. records per-evaluation data with an IOH Analyzer logger
 3. patches the generated IOHprofiler metadata files so they report the custom suite name SlabDesignBench.
 4. optionally zips the result folders created by this call.
"""

SUITE_NAME = "SlabDesignBench"


def _zip_folders(folders: list[Path], zip_path: Path, base_dir: Path) -> None:
    """Zip the given folders into zip_path, preserving paths relative to base_dir."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for folder in folders:
            for file in folder.rglob("*"):
                if file.is_file():
                    zf.write(file, arcname=file.relative_to(base_dir))


def run_experiment(
    problem_bundle: dict[str, dict],
    algorithm,
    n_runs: int,
    name: str = "",
    zip_results: bool = True,
    delete_after_zip: bool = False,
):
    out_root = Path(os.getcwd()) / "logger_results"
    out_root.mkdir(parents=True, exist_ok=True)

    # snapshot existing JSONs so we only patch the ones written this call
    pre_existing = set(out_root.rglob("IOHprofiler_f*.json"))
    # snapshot existing folders so we only zip the ones written this call
    pre_existing_folders = {p.name for p in out_root.iterdir() if p.is_dir()}

    for problem_id, bundle in problem_bundle.items():
        problem = bundle["problem"]
        eval_context = bundle["ctx"]
        var_names = bundle["var_names"]
        constraint_names = bundle["active_constraint_names"]

        eval_context.ensure_constraints(constraint_names)
        eval_context.ensure_params(var_names)
        print("Logging root:", out_root.resolve(), "\n")

        if name == "":
            folder_name = "my_benchmarking_study"
        else:
            folder_name = name

        trigger_alw = [ltr.Each(1)]
        logger = ioh.logger.Analyzer(
            root=str(out_root),
            folder_name=folder_name,
            algorithm_name=algorithm.name,
            algorithm_info=getattr(algorithm, "info", "No additional information provided"),
            store_positions=True,
            triggers=trigger_alw,
        )
        logger.watch(eval_context, "y")
        logger.watch(eval_context, "y_p")
        logger.watch(eval_context, "misses")
        logger.watch(eval_context, "hits")

        for constr in constraint_names:
            logger.watch(eval_context, f"c__{constr}")

        for var in var_names:
            logger.watch(eval_context, f"var__{var}")

        problem.attach_logger(logger)

        for run in range(n_runs):
            algorithm(problem)
            print(f"[{problem.meta_data.name} run {run + 1} - best found:{problem.state.current_best.y: .3f}")
            best_x_overall = list(problem.state.current_best.x)
            eval_context.reset()
            problem.reset()
            _ = problem(best_x_overall)

        problem.detach_logger()
        logger.close()

        # patch suite name into newly written JSONs
        new_jsons = set(out_root.rglob("IOHprofiler_f*.json")) - pre_existing
        for jf in new_jsons:
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                data["suite"] = SUITE_NAME
                jf.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception as e:
                print(f"[warn] could not patch suite name in {jf.name}: {e}")

    # ---- zip the result folders created during this call ----
    if zip_results:
        new_folders = [
            p for p in out_root.iterdir()
            if p.is_dir() and p.name not in pre_existing_folders
        ]
        if new_folders:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = folder_name if name else "experiment"
            zip_path = out_root / f"{base}_{timestamp}.zip"
            _zip_folders(new_folders, zip_path, out_root)
            print(f"\nZipped {len(new_folders)} folder(s) to: {zip_path}")

            if delete_after_zip:
                for folder in new_folders:
                    shutil.rmtree(folder, ignore_errors=True)
                print("Removed source folders after zipping.")
        else:
            print("\nNo new folders to zip.")