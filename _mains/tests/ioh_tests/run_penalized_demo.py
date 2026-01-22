from core.ioh_core.algorithms import NloptDirectSearch
from core.ioh_core.experiment import run_experiment
from core.ioh_core.problem_builder import build_problems_for_slab_type


slab_type = "hp_slab"
bundles = build_problems_for_slab_type(slab_type)

max_evaluations_ = 2
n_runs_ = 1

"DIRECT"
algo = NloptDirectSearch(max_evaluations=max_evaluations_)
run_experiment(bundles, algo, n_runs=n_runs_)