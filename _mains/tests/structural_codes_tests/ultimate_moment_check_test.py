from matplotlib import pyplot as plt

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction
from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE

UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction, 
    test_loads, 
    "SIMPLE_BEAM",
    "MAX_POS_MOMENT")