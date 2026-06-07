from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1, \
    test_slab_construction_c1_2_c50, test_slab_construction_c1_2_c80, test_slab_construction_c1_3
from core.analysis_core.checks.structural_checks import DeflectionLimitByDeflectionCheckEC2004DE
from core.analysis_core.statics.constants import SystemType

"""
Author: Elliot Melcer
Testing the calculation of ba1 utilization:

Passed: 10.02.2026

Methodology:
 1. Run deflection_verification.py
 2. Use Printout as input for the Grasshopper Function "M-Kappa V2" 
 3. Plug Deflection into B.1a Check in Grasshopper -> Util GH
 4. Run this file: -> Util Python
 5. Compare Utilization


Results:

Config   | Util GH  | Util Python* |  Diff
---------+----------+--------------+-------
c1_1     |   0.317  |     0.299    |   -6.0 % 
c1_2_c50 |  -0.308  |    -0.310    |   +0.5 % 
c1_2_c80 |  -0.252  |    -0.255    |   +1.2 %   
c1_3     |   0.170  |     0.505    | +197.0 %   
c1_4     |  -0.311  |    -0.311    |    0.0 %

*raw utilization

"""

# --- Check ---
util = DeflectionLimitByDeflectionCheckEC2004DE.calculate_utilization(
    test_slab_construction_c1_4,
    test_loads,
    system = SystemType.SIMPLE_BEAM,
    limit_factor=250.,
    debug = True
    )

print(f"screened util = {util:.3f}")
