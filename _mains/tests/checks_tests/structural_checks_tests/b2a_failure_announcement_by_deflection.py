from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1, \
    test_slab_construction_c1_2_c50, test_slab_construction_c1_2_c80, test_slab_construction_c1_3
from core.analysis_core.checks.structural_checks import FailureAnnouncementByDeflectionCheckEC2004DE
from core.analysis_core.statics import SystemType

"""
Testing of B.2a Failure Announcement by Deflection

Methodology:
 1. Run deflection_verification.py
 2. Use Printout as input for the Grasshopper Function "M-Kappa V2" 
 3. Plug Deflection into B.2a Check in Grasshopper -> Util GH
 4. Run this file: -> Util Python
 5. Compare Utilization

Note: Utilization is given before as raw w_min/w

Results:

Config   | Util Python | Util GH  |  Diff
---------+-------------+----------+-------
c1_1     |     1.11    |    0.92  | -17 %
c1_2_c50 |   -21.48    |  -22.59  |   5 %
c1_2_c80 |   -25.62    |  -28.34  |  11 %
c1_3     |     2.68    |    3.83  |  43 %
c1_4     |   -10.35    |  -10.49  |   1 %
  

passed: 03.03.26
"""

util = FailureAnnouncementByDeflectionCheckEC2004DE.calculate_utilization(
    test_slab_construction_c1_1,
    test_loads,
    system = SystemType.SIMPLE_BEAM,
    min_factor = 100.,
    debug = True
    )