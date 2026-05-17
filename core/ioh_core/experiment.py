import os
from pathlib import Path
from ioh.iohcpp.logger import trigger as ltr
import ioh


def run_experiment(problem_bundle: dict[str, dict], algorithm, n_runs: int):
    out_root = Path(os.getcwd()) / "logger_results"
    out_root.mkdir(parents=True, exist_ok=True)

    for problem_id, bundle in problem_bundle.items():
        problem = bundle["problem"]
        eval_context = bundle["ctx"]
        var_names = bundle["var_names"]
        constraint_names = bundle["active_constraint_names"]

        eval_context.ensure_constraints(constraint_names)
        eval_context.ensure_params(var_names)
        print("Logging root:", out_root.resolve(),"\n")

        trigger_alw = [ltr.Each(1)]
        logger = ioh.logger.Analyzer(
            root=str(out_root),
            folder_name="my-experiment",
            algorithm_name=algorithm.name,
            store_positions=False,
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