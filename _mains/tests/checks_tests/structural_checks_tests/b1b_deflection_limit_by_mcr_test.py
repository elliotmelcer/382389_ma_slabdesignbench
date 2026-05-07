# --- Check ---
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1
from core.analysis_core.checks.structural_checks import DeflectionLimitByMcrCheckEC2004DE

"""
Testing of B.1b Deflection Limit Check by Cracking Moment

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |    0.120    |  0.120 
c1_1   |    0.692    |  0.703   

passed: 17.02.2026
"""

print("Testing of B.1b Deflection Limit Check by Cracking Moment")
util = DeflectionLimitByMcrCheckEC2004DE.calculate_utilization(
    test_slab_construction_c1_4,
    test_loads,
    system = "SIMPLE_BEAM",
    moment = "MAX_POS_MOMENT",
    debug = True
    )