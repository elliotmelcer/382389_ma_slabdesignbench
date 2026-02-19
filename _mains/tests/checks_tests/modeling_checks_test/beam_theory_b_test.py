"""
Testing of Z.3. Beam-Theory-B/L-Ratio-Check

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_1   |  0.8888     |  0.8888
c1_4   |  0.8888     |  0.8888

passed: 19.02.2026
"""
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_4
from core.analysis_core.checks.modeling_checks import BeamTheoryBLRatioCheck

print("Testing of Z.3. Beam Theory B / L - Ratio Check \n")
util = BeamTheoryBLRatioCheck.calculateUtilization(
    test_slab_construction_c1_1
    )

print(f"c1_util = {util}")

util = BeamTheoryBLRatioCheck.calculateUtilization(
    test_slab_construction_c1_4
    )

print(f"c4_util = {util}")
