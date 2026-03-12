import matplotlib.pyplot as plt
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_hp_sections import hp_section_c2_uls_x_0_50, hp_section_c1_3_uls
from core.analysis_core.section_methods import calculate_moment_curvature_sls, calculate_bending_strength_sls_Nmm, \
    get_concrete, sls_section
from core.visualization_core.visualization import plot_moment_curvature, plot_constitutive_law_concrete

"""
This file is used to show that the structural codes function calculate_moment_curvature() stops when concrete reaches fctm 

When you specify fctm =/= 0, structural codes only stops when reinforcement fails. 
"""


# Section Known to be governed by reinforcement
conc_governed_sec = hp_section_c1_3_uls # C50/60

# SLS Sections
conc_governed_sec_sls_tension = sls_section(conc_governed_sec, True)
conc_governed_sec_sls         = sls_section(conc_governed_sec, False)

# Plot Constitutive Law
plot_constitutive_law_concrete(get_concrete(conc_governed_sec_sls_tension))
plot_constitutive_law_concrete(get_concrete(conc_governed_sec_sls))

mk_conc_gov_tension = calculate_moment_curvature_sls(conc_governed_sec_sls_tension, concrete_tension=True)
mk_conc_gov         = calculate_moment_curvature_sls(conc_governed_sec_sls,         concrete_tension=False)

# --- M-K-results_c2 ---

# print
plot_moment_curvature(mk_conc_gov_tension, x = 0.5, title = "fctm =/= 0")
plot_moment_curvature(mk_conc_gov,         x = 0.5, title = "fctm = 0")

# M_u_sls
m_u_conc_gov_tension = calculate_bending_strength_sls_Nmm(conc_governed_sec_sls_tension)
m_u_conc_gov         = calculate_bending_strength_sls_Nmm(conc_governed_sec_sls)

# Kappa_u_sls
_,kappa_u_conc_gov_tension,_ = m_u_conc_gov_tension.get("strain_profile", (None, None, None))
_,kappa_u_conc_gov        ,_ = m_u_conc_gov.get(        "strain_profile", (None, None, None))

print("Fctm =/= 0:")
print(f"M_u_sls: {m_u_conc_gov_tension["m_u"] * (-10**-6):.2f} kNm")
print(f"Kappa: {kappa_u_conc_gov_tension * -10**6:.2f} 1/m\n")

print("Fctm = 0")
print(f"M_u_sls: {m_u_conc_gov["m_u"] * (-10**-6):.2f} kNm")
print(f"Kappa: {kappa_u_conc_gov * -10**6:.2f} 1/m")

plt.show()