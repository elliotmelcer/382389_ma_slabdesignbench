from matplotlib import pyplot as plt

from _mains.testing_files.testing_floor import test_floor
from _mains.testing_files.testing_hp_sections import hp_section_kappa_0_m2, hp_shell_kappa_0_m2
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_materials import infill
from _mains.verification.kappa_0_compare_0_and_60_pre_lvls import create_section_with_prestress
from core.analysis_core.checks.structural_checks import StructuralCheck, DeflectionLimitByDeflectionCheckEC2004DE
from core.analysis_core.section_methods import calculate_moment_curvature_sls_EC
from core.analysis_core.statics.deflection import DeflectionCalculator
from core.visualization_core.visualization import PlotLine, plot_moment_curvature
from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.hp_model.hp_slab import HPSlab

"""
Testing the boundaries of the new kappa_0 method that only uses the previous secondary method
"""

section = create_section_with_prestress(0.60, "c1_4")

mk_res = calculate_moment_curvature_sls_EC(section, simplification=4)

plot_moment_curvature(mk_res)

plt.show()

fail_section = hp_section_kappa_0_m2

hp_slab_c1_3_uls        = HPSlab(hp_shell_kappa_0_m2, infill)
slab_con = SlabConstruction(hp_slab_c1_3_uls, test_floor)
#
# deflection = DeflectionCalculator.calculate_deflection_mm_EC(slab_con, test_loads)
#
# print(deflection)

eta_deflection = DeflectionLimitByDeflectionCheckEC2004DE.calculate_utilization(
    slab_con,
    test_loads
)

print(eta_deflection)