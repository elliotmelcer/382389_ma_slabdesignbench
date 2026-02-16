# --- Check ---
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction
from core.analysis_core.checks.structural_checks import DeflectionLimitByMcrCheckEC2004DE

util = DeflectionLimitByMcrCheckEC2004DE.calculateUtilization(
    test_slab_construction,
    test_loads,
    system = "SIMPLE_BEAM",
    moment = "MAX_POS_MOMENT",
    debug = True
    )

print(f"util = {util:.3f}")