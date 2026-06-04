from matplotlib import pyplot as plt
from shapely import Polygon
from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement_line
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_hp_sections import hp_section_c1_3_uls
from _mains.testing_files.testing_materials import reinforcement_B500
from core.analysis_core.section_methods import calculate_moment_curvature_sls_EC, sls_section_EC, get_concrete
from core.visualization_core.visualization import plot_cross_section, PlotLine, plot_moment_curvature_multiple, \
    TU_COLORS, plot_constitutive_law_concrete, plot_constitutive_law_reinforcement

plt.rcParams["font.family"] = "STIXGeneral"
set_design_code('ec2_2004')

h = 300
b = 1000
d = 30
fck = 30
d_p = 20
n_p = 10
kappa_t = 0.0
c_nom = 30

"concrete"
point_list = [
    (-b/2, -h/2),
    (-b/2,  h/2),
    ( b/2,  h/2),
    ( b/2, -h/2),
]

polygon = Polygon(point_list)

concrete = create_concrete(fck)

"reinforcement"
reinf = reinforcement_B500

# - Definition
reinforcement_B500_ep = create_reinforcement(
    fyk=500,
    Es=200_000,
    ftk=550,
    epsuk=0.07,
    density=7850,
    constitutive_law="elasticplastic")

# - Definition
reinforcement_B500_epp = create_reinforcement(
    fyk=500,
    Es=200_000,
    ftk=550,
    epsuk=0.07,
    density=7850,
    constitutive_law="elasticperfectlyplastic")

# - Definition
reinforcement_B500_e = create_reinforcement(
    fyk=500,
    Es=200_000,
    ftk=550,
    epsuk=0.07,
    density=7850,
    constitutive_law="elastic"
)

reinf_start = (-b/2+c_nom+d_p/2  ,  -h/2+d+d_p/2)
reinf_end =   ( b/2-c_nom-d_p/2   ,  -h/2+d+d_p/2)

"concrete section"
geometry = SurfaceGeometry(
    poly=polygon, material=concrete, concrete = True
)
geometry = add_reinforcement_line(geometry, reinf_start, reinf_end, d_p, reinforcement_B500, n_p)
# section = GenericSection(geometry, integrator='marin')
section = hp_section_c1_3_uls

# "moment-curvature-diagram"
# mkd_none            = calculate_moment_curvature_sls_EC(section, constitutive_law = "NONE_PARABOLIC"    )
# mkd_fctm            = calculate_moment_curvature_sls_EC(section, constitutive_law = "FCTM_PARABOLIC"    )
# mkd_tenstiff        = calculate_moment_curvature_sls_EC(section, constitutive_law = "TENSTIFF_PARABOLIC")
# mkd_tenstiff_simp   = calculate_moment_curvature_sls_EC(section, constitutive_law = "TENSTIFF_PARABOLIC", simplification=True)
#
# mkd_line_none           = PlotLine.from_results(mkd_none            , color = TU_COLORS["RED"], name = "NONE_PARABOLIC"    )
# mkd_line_fctm           = PlotLine.from_results(mkd_fctm            , color = TU_COLORS["BLUE"], name = "FCTM_PARABOLIC"    )
# mkd_line_tenstiff       = PlotLine.from_results(mkd_tenstiff        , color = TU_COLORS["VIOLET"], name = "TENSTIFF_PARABOLIC")
# mkd_line_tenstiff_simp  = PlotLine.from_results(mkd_tenstiff_simp   , color = TU_COLORS["ORANGE"], name = "simplification = True", marker="o", linestyle = "none")
#
# lines = [
#     mkd_line_none    ,
#     mkd_line_fctm    ,
#     mkd_line_tenstiff,
#     mkd_line_tenstiff_simp
# ]

"constitutive laws"
sls_section_none          = sls_section_EC(section, "NONE_PARABOLIC")
sls_section_fctm          = sls_section_EC(section, "FCTM_PARABOLIC")
sls_section_tenstiff      = sls_section_EC(section, "TENSTIFF_PARABOLIC")
sls_section_elastic       = sls_section_EC(section, "ELASTIC_ELASTIC")

conc_none           = get_concrete(sls_section_none    )
conc_fctm           = get_concrete(sls_section_fctm    )
conc_tenstiff       = get_concrete(sls_section_tenstiff)
conc_elastic       = get_concrete(sls_section_elastic)

"plots"
# plot_moment_curvature_multiple(lines)
# plot_cross_section(section)

plot_constitutive_law_concrete(conc_none        )
plot_constitutive_law_concrete(conc_fctm        )
plot_constitutive_law_concrete(conc_tenstiff    )
plot_constitutive_law_concrete(conc_elastic     )

plot_constitutive_law_reinforcement(reinforcement_B500_ep)
plot_constitutive_law_reinforcement(reinforcement_B500_epp)
plot_constitutive_law_reinforcement(reinforcement_B500_e)


plt.show()