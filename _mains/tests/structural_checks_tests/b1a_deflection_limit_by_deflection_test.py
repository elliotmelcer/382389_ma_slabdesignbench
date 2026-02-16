from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from core.analysis_core.checks.structural_checks import DeflectionLimitByDeflectionCheckEC2004DE

"""
Author: Elliot Melcer
Testing the calculation of ba1 utilization:

Passed: 10.02.2026
"""

# --- Check ---
util = DeflectionLimitByDeflectionCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_4,
    test_loads,
    system = "SIMPLE_BEAM",
    limit_factor=250.,
    debug = True
    )

print(f"util = {util:.3f}")
