from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1
from core.analysis_core.checks.structural_checks import FailureAnnouncementByDeflectionCheckEC2004DE

"""
Testing of B.2a Failure Announcement by Deflection

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |   99.000    |  
c1_1   |    1.109    |     

passed: 
"""

util = FailureAnnouncementByDeflectionCheckEC2004DE.calculateUtilization(
    test_slab_construction_c1_4,
    test_loads,
    system = "SIMPLE_BEAM",
    min_factor = 100.,
    debug = True
    )

print(f"util = {util:.3f}")