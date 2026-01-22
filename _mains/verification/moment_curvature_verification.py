from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c2_uls_x_0_00, hp_section_c2_uls_x_0_10, \
    hp_section_c2_uls_x_0_20, hp_section_c2_uls_x_0_30, hp_section_c2_uls_x_0_40, hp_section_c2_uls_x_0_50
from core.analysis_core.section_methods import calculate_moment_curvature_sls
from core.visualization_core.visualization import plot_moment_curvature

"""
This file is used for verification of the moment-curvature-diagrams. 

The section used for verification is from chapter "C.2.  Vergleich der M-κ-Diagramme" in Loutfi (2023)

passed 29.12.2025

Output:

See plots

"""

moment_curvature_c2_x_0_00 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_00)
moment_curvature_c2_x_0_10 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_10)
moment_curvature_c2_x_0_20 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_20)
moment_curvature_c2_x_0_30 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_30)
moment_curvature_c2_x_0_40 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_40)
moment_curvature_c2_x_0_50 = calculate_moment_curvature_sls(hp_section_c2_uls_x_0_50)

# --- M-K-results_c2 ---

# print
plot_moment_curvature(moment_curvature_c2_x_0_00, x = 0.00)
plot_moment_curvature(moment_curvature_c2_x_0_10, x = 0.10)
plot_moment_curvature(moment_curvature_c2_x_0_20, x = 0.20)
plot_moment_curvature(moment_curvature_c2_x_0_30, x = 0.30)
plot_moment_curvature(moment_curvature_c2_x_0_40, x = 0.40)
plot_moment_curvature(moment_curvature_c2_x_0_50, x = 0.50)

# table
# print(table_moment_curvature(moment_curvature_c2))

# --- show ---
plt.show()

