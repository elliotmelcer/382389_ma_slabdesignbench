"""
Testing of Z.2. Beam-Theory-H_ges/L-Ratio-Check

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_1   |  0.1481     |  0.1481
c1_4   |  0.3703     |  0.3703

passed: 19.02.2026
"""
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_4
from core.analysis_core.checks.modeling_checks import BeamTheoryHgesLRatioCheck

print("Testing of Z.2. Beam Theory H_ges / L - Ratio Check \n")
util = BeamTheoryHgesLRatioCheck.calculateUtilization(
    test_slab_construction_c1_1
    )

print(f"c1_util = {util}")

util = BeamTheoryHgesLRatioCheck.calculateUtilization(
    test_slab_construction_c1_4
    )

print(f"c4_util = {util}")
