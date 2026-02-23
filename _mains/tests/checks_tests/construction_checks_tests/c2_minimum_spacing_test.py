"""
Testing of C.2. Sufficient Reinforcement Spacing

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |    1.4465   | 1.4465
c1_1   |    0.7754   | 0.7754

passed: 18.02.2026
"""
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1
from core.analysis_core.checks.construction_checks import ReinforcementSpacingCheck

print("Testing of C.2. Sufficient Reinforcement Spacing")
util = ReinforcementSpacingCheck.calculateUtilization(
    test_slab_construction_c1_4,
    debug_print=True
    )

print(f"c2_util = {util}")
