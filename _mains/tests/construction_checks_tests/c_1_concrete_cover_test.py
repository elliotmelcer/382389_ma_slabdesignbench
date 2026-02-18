"""
Testing of C.1. Sufficient Concrete Cover

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |   0.2467    |  0.2467
c1_1   |   0.2229    |  0.2229

passed: 18.02.2026
"""
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_4
from core.analysis_core.checks.construction_checks import MidlineConcreteCoverCheck

print("Testing of C.1. Sufficient Concrete Cover")
util = MidlineConcreteCoverCheck.calculateUtilization(
    test_slab_construction_c1_4
    )

print(f"c_1_util = {util}")
