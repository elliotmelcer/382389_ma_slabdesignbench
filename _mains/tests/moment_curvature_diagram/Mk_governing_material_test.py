import matplotlib.pyplot as plt
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_hp_sections import hp_section_c2_uls_x_0_50, hp_section_c1_3_uls
from core.analysis_core.section_methods import calculate_moment_curvature_sls, calculate_bending_strength_sls_Nmm, \
    get_concrete, sls_section
from core.visualization_core.visualization import plot_moment_curvature

"""
This file is used to show the differences in moment-curvature-diagrams when handling concrete- vs. reinforcement-governed sections.

This demonstration shows, that a concrete governed MK Diagram would stops after concrete reaches fcm(sargin)/fck(parabola-rectangle) plateau IF num_post_yield = 0. 

Changes were made in section_methods.py/calculate_moment_curvature_sls() to continue on after reaching that point, by controlling num_post_yield
according to which material is governing.  
"""


# Section Known to be governed by reinforcement or concrete
reinf_governed_sec = hp_section_c2_uls_x_0_50 # C50/60
conc_governed_sec = hp_section_c1_3_uls # C50/60

# SLS Sections
reinf_governed_sec_sls = sls_section(reinf_governed_sec, "NONE_PARABOLIC")
conc_governed_sec_sls = sls_section(conc_governed_sec, "NONE_PARABOLIC")

mk_reinf_gov = calculate_moment_curvature_sls(reinf_governed_sec, 0.0, "NONE_PARABOLIC")
mk_conc_gov = calculate_moment_curvature_sls(conc_governed_sec, 0.0, "NONE_PARABOLIC")

# --- M-K-results_c2 ---

# print
plot_moment_curvature(mk_reinf_gov, x = 0.5, title = "Reinforcement Governing")
plot_moment_curvature(mk_conc_gov,  x = 0.5, title = "Concrete Governing")

# M_u_sls
m_u_reinf_gov = calculate_bending_strength_sls_Nmm(reinf_governed_sec)
m_u_conc_gov = calculate_bending_strength_sls_Nmm(conc_governed_sec)

# Kappa_u_sls
_,kappa_u_reinf_gov,_ = m_u_reinf_gov.get("strain_profile", (None, None, None))
_,kappa_u_conc_gov,_ = m_u_conc_gov.get("strain_profile", (None, None, None))

print("Reinforcement governed design:")
print(f"M_u_sls (reinf. gov.): {m_u_reinf_gov["m_u"] * (-10**-6):.2f} kNm")
print(f"Kappa (reinf. gov.): {kappa_u_reinf_gov * -10**6:.2f} 1/m\n")

print("Concrete governed design")
print(f"M_u_sls (conc. gov.): {m_u_conc_gov["m_u"] * (-10**-6):.2f} kNm")
print(f"Kappa (conc. gov.): {kappa_u_conc_gov * -10**6:.2f} 1/m")

plt.show()