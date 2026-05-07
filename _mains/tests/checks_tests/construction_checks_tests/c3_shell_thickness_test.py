"""
Testing of C.3. Minimum Shell Thickness

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |    1.3877   | 1.3877
c1_1   |    2.7427   | 2.7427

passed: 18.02.2026
"""

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1
from core.analysis_core.checks.construction_checks import MinimumHPShellThicknessCheck

print("Testing of C.3. Minimum Shell Thickness")
util = MinimumHPShellThicknessCheck.calculate_utilization(
    test_slab_construction_c1_4
    )

print(f"c2_util = {util}")
