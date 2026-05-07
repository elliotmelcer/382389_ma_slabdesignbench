"""
Testing of C.1. Sufficient Concrete Cover from the outermost Reinforcement to the Edge along the HP-Shell Midline

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_1   |   0.2229    |  0.2229
c1_4   |   0.2467    |  0.2467

passed: 18.02.2026
"""
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_4
from core.analysis_core.checks.construction_checks import MidlineConcreteCoverCheck

print("Testing of C.1. Sufficient Concrete Cover \n")
util = MidlineConcreteCoverCheck.calculate_utilization(
    test_slab_construction_c1_1
    )

print(f"c1_util = {util}")

util = MidlineConcreteCoverCheck.calculate_utilization(
    test_slab_construction_c1_4
    )

print(f"c4_util = {util}")
