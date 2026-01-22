from matplotlib import pyplot as plt
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.sections import GenericSection

from core.analysis_core import section_methods
from core.analysis_core.section_methods import sls_section, get_concrete
from core.visualization_core.visualization import plot_moment_curvature, plot_constitutive_law_concrete, \
    plot_constitutive_law_reinforcement, table_moment_curvature, plot_cross_section
from slab_construction.slabs import HPSlab
from _mains.testing_files.testing_materials import solidian_Q142_pre_50, concrete_c50_uls

# hp_geometry stuff
b  = 1200      #mm
l = 6750      #mm
hx = 70        # mm
hy = 280       #mm
t   = 40        #mm
dy = 30         #mm
nt = 5          #-

x = 0.0 # * l

hp = HPSlab(B = b, L = l, Hx = hx, Hy = hy, t = t, dy = dy, nt = nt)

# structural codes stuff

# --- concrete section ---
hp_geometry = SurfaceGeometry(
    poly=hp.polygon_section_at(x = x, n = 100), material=concrete_c50_uls
)

# --- reinforcement ---
reinforcement_points = hp.tendon_coords_at_x(x = x)

for pt in reinforcement_points:
    hp_geometry = add_reinforcement(
        hp_geometry,
        pt,       # reinforcement points
        3.56825,        # diameter [mm]
        solidian_Q142_pre_50  # reinforcement material
    )

hp_section = GenericSection(hp_geometry)
hp_section_sls = sls_section(hp_section)

moment_curvature = hp_section.section_calculator.calculate_moment_curvature()

print("Mcr (SLS) = ",section_methods.calculate_cracking_moment_sls_prestressed(hp_section_sls, n=0)/1000000, " kNm\n")

# print(section_methods.calculate_cracking_moment(hp_section, n=0))
# print(section_methods.calculate_cracking_moment_manual(hp_section))


# --- constitutive laws ---

# prints
print('Beton Arbeitslinie: ', concrete_c50_uls.constitutive_law)
print('CFK Arbeitslinie: ', solidian_Q142_pre_50.constitutive_law)

# plots
plot_constitutive_law_concrete(concrete_c50_uls)
plot_constitutive_law_concrete(get_concrete(hp_section_sls))
plot_constitutive_law_reinforcement(solidian_Q142_pre_50)

# --- cross-section ---
plot_cross_section(hp_section, x = x/l)


# --- M-K-results_c1_1 ---

# print
plot_moment_curvature(moment_curvature, x = x/l)

# table
print(table_moment_curvature(moment_curvature))

# --- show ---
plt.show()

