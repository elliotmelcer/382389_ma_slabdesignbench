from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import (
    test_slab_construction_c1_1,
    test_slab_construction_c1_2_c50,
    test_slab_construction_c1_2_c80,
    test_slab_construction_c1_3,
    test_slab_construction_c1_4,
    test_slab_construction_ref,
)
from core.analysis_core.statics import SystemType, MomentType

"""
Testing of A Ultimate Moment

Results:

Config   | Util Python | Util GH  |  Diff
---------+-------------+----------+---------
c1_1     |    1.069    |   1.048  |  -1.96 %
c1_2_c50 |    0.348    |   0.345  |  -0.86 %
c1_2_c80 |    0.307    |   0.295  |  -3.91 %
c1_3     |    0.421    |   0.408  |  -3.09 %
c1_4     |    0.181    |   0.178  |  -1.66 %
 

passed: 08.03.26
"""

test_cases = {
    "C1_1": test_slab_construction_c1_1,
    "C1_2_c50": test_slab_construction_c1_2_c50,
    "C1_2_c80": test_slab_construction_c1_2_c80,
    "C1_3": test_slab_construction_c1_3,
    "C1_4": test_slab_construction_c1_4,
}

print("Testing Check A: Ultimate Moment")

for name, slab_construction in test_cases.items():
    util = UltimateMomentCheckEC2004DE.calculate_utilization(
        slab_construction,
        test_loads,
        SystemType.SIMPLE_BEAM,
        MomentType.MAX_POS_MOMENT,
        debug_print=False,
    )
    print(f"util {name:<8}: {util:.3f}")