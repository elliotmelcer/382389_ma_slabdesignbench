from matplotlib import pyplot as plt

from _mains.testing_files.testing_sections import t_section
from core.analysis_core import section_methods
from core.visualization_core.visualization import plot_constitutive_law_concrete, \
    plot_constitutive_law_reinforcement, plot_cross_section
from _mains.testing_files.testing_materials import reinforcement_B500, concrete_c40_uls

wy_verification_section = t_section
# moment_curvature = section.section_calculator.calculate_moment_curvature()

print("Mcr (ULS) = ",section_methods.calculate_cracking_moment(wy_verification_section, n=0)/1000000, " kNm\n")
print("Mcr (SLS) = ",section_methods.calculate_cracking_moment_sls(wy_verification_section, n=0)/1000000, " kNm\n")

#
# # --- constitutive laws ---
#
# # prints
print('Beton Arbeitslinie: ', concrete_c40_uls.constitutive_law)
print('Beton Ecm: ', concrete_c40_uls.Ecm)
print('CFK Arbeitslinie: ', reinforcement_B500.constitutive_law)

# # plots
plot_constitutive_law_concrete(concrete_c40_uls)
plot_constitutive_law_reinforcement(reinforcement_B500)
#
# # --- cross-section ---
# plot_cross_section(section, x = 0)
#
#
# # --- M-K-results_c1_1 ---
#
# # print
# plot_moment_curvature(moment_curvature, x = 0)

# --- Plot the triangulated Mesh ---
# integrator = FiberIntegrator()
# tri = integrator.triangulate(geometry, mesh_size=0.01)
# plot_mesh_with_triangles(tri)

# # table
# print(table_moment_curvature(moment_curvature))
#
# # --- show ---
plot_cross_section(wy_verification_section)
plt.show()

