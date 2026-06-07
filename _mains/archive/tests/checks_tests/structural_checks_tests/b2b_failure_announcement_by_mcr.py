from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_4
from core.analysis_core.checks.structural_checks import FailureAnnouncementByMcrCheckEC2004DE
from core.analysis_core.statics.constants import SystemType, MomentType

"""
Testing of B.1b Failure Announcement by Cracking Moment

Results:

Config | Util Python | Util GH
-------+-------------+---------
c1_4   |    4.624    |  4.593
c1_1   |    0.653    |  0.642   

passed: 17.02.2025
"""

util = FailureAnnouncementByMcrCheckEC2004DE.calculate_utilization(
    test_slab_construction_c1_1,
    test_loads,
    system = SystemType.SIMPLE_BEAM,
    moment= MomentType.MAX_POS_MOMENT,
    debug = True
    )

print(f"util = {util:.3f}")