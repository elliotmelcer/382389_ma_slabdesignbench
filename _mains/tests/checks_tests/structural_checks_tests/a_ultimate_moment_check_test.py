from matplotlib import pyplot as plt

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1, \
    test_slab_construction_c1_2_c50, test_slab_construction_c1_2_c80, test_slab_construction_c1_3, \
    test_slab_construction_ref
from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE

util_c1_1 = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_1,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

util_c1_2_c50 = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_2_c50,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

util_c1_2_c80 = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_2_c80,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

util_c1_3 = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_3,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

util_c1_4 = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_4,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

util_ref = UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_ref,
    test_loads,
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT",
    debug_print=False
)

print("Testing Check A: Ultimate Moment")
print(f"util C1_1:      {util_c1_1:.3f}")
print(f"util C1_2_c50:  {util_c1_2_c50:.3f}")
print(f"util C1_2_c80:  {util_c1_2_c80:.3f}")
print(f"util C1_3:      {util_c1_3:.3f}")
print(f"util C1_4:      {util_c1_4:.3f}")
print(f"util Ref :      {util_ref:.3f}")