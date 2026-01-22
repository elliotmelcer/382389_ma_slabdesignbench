from matplotlib import pyplot as plt

from _mains.testing_files.test_slab_two_span import TestSlabTwoWay
from _mains.testing_files.testing_floor import test_floor
from _mains.testing_files.testing_loads import test_loads
from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE
from core.visualization_core.visualization import plot_cross_section
from slab_construction.slab_construction import SlabConstruction

"""
Author: Elliot Melcer
Testing the calculation of ultimate support moment:

Passed: 16.01.2026
"""

# --- Slab ---
test_slab = TestSlabTwoWay(L = 10000)           # 10 m span

plot_cross_section(test_slab.section_at(1.0))   # Section at second support

# --- Slab Construction ---
test_slab_construction_two_span = SlabConstruction(test_slab, test_floor)

# --- Check ---
UltimateMomentCheckEC2004DE.calculateUtilization(
    test_slab_construction_two_span,
    test_loads,
    "TWO_SPAN",
    "MAX_NEG_MOMENT")

# --- Plot Cross Section ---
plt.show()