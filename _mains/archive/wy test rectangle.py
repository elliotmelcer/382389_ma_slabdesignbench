from matplotlib import pyplot as plt
from shapely import Polygon
from structuralcodes.geometry import SurfaceGeometry
from structuralcodes.sections import GenericSection

from core.analysis_core import section_methods
from core.visualization_core.visualization import plot_constitutive_law_concrete, \
    plot_constitutive_law_reinforcement, plot_cross_section
from testing_generics import generic_cfrp_pre, generic_concrete_c50_uls, \
    generic_cfrp, generic_reinforcement, generic_concrete_c40_uls

# hp_geometry stuff
b  = 300      #mm
b1 = 50
b0 = 200
d = 200
d1 = 200
d0 = 400
cover = 50

polygon = Polygon(
    [
        (-b /2,  d/2),
        (-b /2, -d/2),
        ( b /2, -d/2),
        ( b /2,  d/2),
    ]
)

# structural codes stuff

# --- concrete section ---
geometry = SurfaceGeometry(
    poly=polygon, material=generic_concrete_c40_uls
)

section = GenericSection(geometry)
# moment_curvature = section.section_calculator.calculate_moment_curvature()

print("Mcr = ",section_methods.calculate_cracking_moment(section, n=0)/1000000, " kNm\n")

#
# # --- constitutive laws ---
#
# # prints
print('Beton Arbeitslinie: ', generic_concrete_c40_uls.constitutive_law)
print('CFK Arbeitslinie: ', generic_reinforcement.constitutive_law)

# # plots
plot_constitutive_law_concrete(generic_concrete_c40_uls)
plot_constitutive_law_reinforcement(generic_reinforcement)
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
plot_cross_section(section)
plt.show()

