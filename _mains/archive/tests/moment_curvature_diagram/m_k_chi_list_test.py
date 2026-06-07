import numpy as np
from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_3_uls, hp_section_c1_4_uls
from core.analysis_core.section_methods import sls_section_EC
from core.visualization_core.visualization import plot_moment_curvature

chi = np.linspace(-0.00010, 0.000008, 80)

section = hp_section_c1_4_uls
sls_section = sls_section_EC(section, "FCTM_PARABOLIC")

mkd_chi = section.section_calculator.calculate_moment_curvature(chi=chi)
mkd_auto = section.section_calculator.calculate_moment_curvature(num_pre_yield=40,num_post_yield=40)

plot_moment_curvature(mkd_chi)
plot_moment_curvature(mkd_auto)

plt.show()