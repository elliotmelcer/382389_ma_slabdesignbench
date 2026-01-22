import os
from pathlib import Path
from ioh.iohcpp.logger import trigger as ltr
import ioh


def run_experiment(problem_bundle: dict[str, dict], algorithm, n_runs: int):
    out_root = Path(os.getcwd()) / "logger_results"
    out_root.mkdir(parents=True, exist_ok=True)

    for pid, b in problem_bundle.items():
        p = b["problem"]
        ctx = b["ctx"]
        var_names = b["var_names"]
        constraint_names = b["active_constraint_names"]

        ctx.ensure_constraints(constraint_names)
        ctx.ensure_params(var_names)
        print("Logging root:", out_root.resolve())

        trigger_alw = [ltr.Each(1)]
        lg = ioh.logger.Analyzer(
            root=str(out_root),
            folder_name="my-experiment",
            algorithm_name=algorithm.name,
            store_positions=False,
            triggers=trigger_alw,
        )
        lg.watch(ctx, "y")
        lg.watch(ctx, "y_p")
        lg.watch(ctx, "misses")
        lg.watch(ctx, "hits")

        for c in constraint_names:
            lg.watch(ctx, f"c__{c}")

        for v in var_names:
            lg.watch(ctx, f"var__{v}")

        p.attach_logger(lg)

        for run in range(n_runs):
            algorithm(p)
            print(f"[{p.meta_data.name} run {run + 1} - best found:{p.state.current_best.y: .3f}")
            best_x_overall = list(p.state.current_best.x)
            ctx.reset()
            p.reset()
            _ = p(best_x_overall)

        p.detach_logger()
        lg.close()