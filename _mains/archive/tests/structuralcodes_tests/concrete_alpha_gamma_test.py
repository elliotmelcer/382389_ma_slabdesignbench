from matplotlib import pyplot as plt
from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_materials import reinforcement_B500
from _mains.testing_files.testing_sections import t_section_polygon
from core.analysis_core.material_methods import fctm_parabolic_law_EC
from core.analysis_core.section_methods import calculate_moment_curvature_sls_EC
from core.visualization_core.visualization import plot_constitutive_law_concrete, plot_moment_curvature

"""
This tests studies the influence of alpha_cc and gamma_c on the results for SLS and ULS 
concrete sections

Results:

SLS: 
 - fctm_parabolic_law() method used
 - default values: alpha_cc = 1.0, gamma_c = 1.5
 - alpha_cc and gamma_c do NOT affect constitutive law, ultimate strength or mkd

ULS:
 - 'parabolarectangle' used
 - default values: alpha_cc = 1.0, gamma_c = 1.5
 - AFFECTS 'parabola_rectangle' c.law,  ultimate strength, and mkd
"""

set_design_code('ec2_2004')

c = create_concrete(fck=30,
                    constitutive_law=fctm_parabolic_law_EC(30),
                    name = "c")

c_alpha = create_concrete(fck=30, constitutive_law=fctm_parabolic_law_EC(30),
                          alpha_cc = 1.0,
                          gamma_c=1.0,
                          name="c_alpha")


section_polygon = t_section_polygon

# structural codes stuff

# --- concrete section ---
geo = SurfaceGeometry(
    poly=t_section_polygon, material=c
)

geo_alpha = SurfaceGeometry(
    poly=t_section_polygon, material=c_alpha
)

def add_reinf(geometry: SurfaceGeometry) -> GenericSection:
    b  = 300      #mm
    b1 = 50
    b0 = 200
    d = 200
    d1 = 200
    cover = 50

    # --- reinforcement ---
    geometry = add_reinforcement(
        geometry,
        (
            -b0/2+cover, -d/2 - d1 + cover
        ),
        20,
        reinforcement_B500,
    )  # The add_reinforcement function returns a CompoundGeometry
    geometry = add_reinforcement(
        geometry,
        (
            0, -d1-cover
        ),
        20,
        reinforcement_B500,
    )
    geometry = add_reinforcement(
        geometry,
        (
            b0/2-cover, -d/2 - d1 + cover
        ),
        20,
        reinforcement_B500,
    )

    return GenericSection(geometry, integrator='marin')

section = add_reinf(geo)
section_alpha = add_reinf(geo_alpha)

# Moment Curvature Diagram

# mk_res = section.section_calculator.calculate_moment_curvature(
#         n=0.0,
#         num_pre_yield=40,
#         num_post_yield=40
#     )
#
# mk_res_alpha = section_alpha.section_calculator.calculate_moment_curvature(
#         n=0.0,
#         num_pre_yield=40,
#         num_post_yield=40
#     )

# Ultimate Strength

m_u = section.section_calculator.calculate_bending_strength(n=0)
m_u_alpha = section_alpha.section_calculator.calculate_bending_strength(n=0)

# PLots
print("c :", c.alpha_cc, c.gamma_c, c.Ecm)
print("c_alpha: ", c_alpha.alpha_cc, c_alpha.gamma_c, c_alpha.Ecm)

plot_constitutive_law_concrete(c)
plot_constitutive_law_concrete(c_alpha)

print("c : M_u= ",      m_u_alpha.m_y)
print("c_alpha: M_u= ", m_u.m_y)

# plot_moment_curvature(mk_res, title="mk_res")
# plot_moment_curvature(mk_res_alpha, title = "mk_res_alpha")


plt.show()