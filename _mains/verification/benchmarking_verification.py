import time
from contextlib import contextmanager

from core.ioh_core.algorithms import NloptDirectLocalSearch, RandomSearch
from core.ioh_core.experiment import run_experiment
from core.ioh_core.problem_builder import build_problems_for_slab_type

"""
Author: Elliot Melcer

Benchmarking script for validating the ioh_core implementation and the HP-slab
optimization problem (see hp_slab/analysis.py).

Runs one or more optimization algorithms on one or more HP-slab problems and writes the
results to disk. 

Control Settings below to choose between a single-algorithm run and a
multi-algorithm comparison (which creates a separate output folder per algorithm).

Note: before running any of the mode, the right .csv-files according to 
the validation chapter of Melcer [2026] need to be placed in the hp_slab-package
"""

# ==============================================================================================
# Settings — edit the mode for the run (don't forget the correct .csv-files)
# ==============================================================================================

MODE = "single_alg"  # Options: "single_alg", "multi_instance", "multi_run" or "multi_alg"

# ==============================================================================================
# Runners
# ==============================================================================================

def run_single_alg():
    """Run one algorithm on the HP-slab problem."""
    print("Running single algorithm on HP-slab problem...")
    bundles = build_problems_for_slab_type("hp_slab")
    algo = NloptDirectLocalSearch(max_evaluations=100)
    run_experiment(
        bundles,
        algorithm = algo,
        n_runs=1,
        name=f"sdb_benchmarking_single_alg_{algo.name}",
        delete_after_zip = True
    )

def run_multi_instance():
    """Run one algorithm on multiple HP-slab problem instances"""
    print("Running one algorithm on multiple HP-slab problem instances...")
    bundles = build_problems_for_slab_type("hp_slab")
    run_experiment(
        bundles,
        algorithm = NloptDirectLocalSearch(max_evaluations=5),
        n_runs=1,
        name="sdb_benchmarking_multi_instance",
        delete_after_zip = True
    )

def run_multi_run():
    """Run one algorithm on the HP-slab problem for multiple runs."""
    print("Running one algorithm on the HP-slab problem for multiple runs...")
    bundles = build_problems_for_slab_type("hp_slab")
    run_experiment(
        bundles,
        algorithm = RandomSearch(max_evaluations=5, seed=0),
        n_runs=5,
        name="sdb_benchmarking_multi_run",
        delete_after_zip = True
    )

def run_multi_alg():
    """Run several algorithms on the HP-slab problem; each gets its own output folder."""
    print("Running several algorithms on HP-slab problem...")
    algos = [
        NloptDirectLocalSearch(max_evaluations=50),
        RandomSearch(max_evaluations=50, seed=0),
    ]

    for algo in algos:
        bundles = build_problems_for_slab_type("hp_slab")
        run_experiment(
            bundles,
            algo,
            n_runs=1,
            name=f"sdb_benchmark_multi_alg_{algo.name}",
            delete_after_zip = True
        )

# ==============================================================================================
# Function for Timing
# ==============================================================================================

@contextmanager
def timed(label: str, enabled: bool = True):
    if not enabled:
        yield
        return
    start = time.perf_counter()
    yield
    print(f"Analysis Time {label}: {time.perf_counter() - start:.6f} s")

# ==============================================================================================
# Entry point
# ==============================================================================================
timer = True

if __name__ == "__main__":
    if MODE == "single_alg":
        with timed("single_alg", timer):
            run_single_alg()
    elif MODE == "multi_instance":
        with timed("multi_instance", timer):
            run_multi_instance()
    elif MODE == "multi_run":
        with timed("multi_run", timer):
            run_multi_run()
    elif MODE == "multi_alg":
        with timed("multi_alg", timer):
            run_multi_alg()
    else:
        raise ValueError(f"Unknown MODE: {MODE!r}. Use 'single_alg', "
                         f"'multi_instance', 'multi_run' or 'multi_alg'.")