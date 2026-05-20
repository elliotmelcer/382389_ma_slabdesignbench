import os

import matplotlib.pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c2_uls_x_0_50, hp_section_c1_3_uls
from core.analysis_core.section_methods import calculate_moment_curvature_sls, sls_section
from core.visualization_core.visualization import plot_moment_curvature, plot_strain_profile

plt.rcParams["font.family"] = "STIXGeneral"

"""
num_post_yield is an input parameter for section.section_calculator.calculate_moment_curvature() in StructuralCodes.
This file can be used to show that IF num_post_yield = 0 the moment-curvature-diagram for a concrete governed section 
would stop when concrete reaches ε_c1. 

To show this effect do the following:

 1. go to section_methods.py
 2. go to _full_moment_curvature_method()
 3. Change: "num_post_yield = 10 if concrete_governs else 0" 
        to: "num_post_yield =  0 if concrete_governs else 0"
                               ^
 4. run this file
 
The strain profile for the last point of the moment-curvature-diagram of the concrete-governed section will show, that
concrete has only reached 2.5 mm/m. Which means that the section has not yet failed under concrete pressure, but the 
moment-curvature-diagram calculation has stopped nonetheless. 
"""

" Run ───────────────────────────────────────────────────────────────────────────────────"
num_post_yield = 0 # change here to show correct num_post_yield in plot title

# Sections known to be governed by reinforcement or concrete─────────────────────────────
reinf_governed_sec = hp_section_c2_uls_x_0_50   # C50/60, reinforcement prestressed 60%
conc_governed_sec = hp_section_c1_3_uls         # C50/60, reinforcement prestressed 0%

# SLS Sections──────────────────────────────────────────────────────────────────────────
reinf_governed_sec_sls = sls_section(reinf_governed_sec, "NONE_PARABOLIC")
conc_governed_sec_sls = sls_section(conc_governed_sec, "NONE_PARABOLIC")

# moment-curvature-diagrams─────────────────────────────────────────────────────────────
mk_reinf_gov = calculate_moment_curvature_sls(reinf_governed_sec, 0.0, "NONE_PARABOLIC")
mk_conc_gov = calculate_moment_curvature_sls(conc_governed_sec, 0.0, "NONE_PARABOLIC")

# Strain Profile for the last point of the moment curvature diagram─────────────────────
m_u_mk_reinf_gov = mk_reinf_gov.m_y[-1]
sp_u_mk_sp_reinf_gov = reinf_governed_sec_sls.section_calculator.calculate_strain_profile(0, m_u_mk_reinf_gov, 0)
mk_u_result_reinf_gov = {
    "section":          reinf_governed_sec_sls,
    "strain_profile":   sp_u_mk_sp_reinf_gov
}

m_u_mk_conc_gov = mk_conc_gov.m_y[-1]
sp_u_mk_sp_conc_gov = conc_governed_sec_sls.section_calculator.calculate_strain_profile(0, m_u_mk_conc_gov, 0)
mk_u_result_conc_gov = {
    "section":          conc_governed_sec_sls,
    "strain_profile":   sp_u_mk_sp_conc_gov
}

# plots─────────────────────────────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")

# moment-curvature-diagrams
fig_1, ax_1 = plot_moment_curvature(mk_reinf_gov, x = 0.5, title = f"C.2: Moment-curvature-diagram for reinforcement governing section \nnum_post_yield = {num_post_yield}")
fig_1.savefig(os.path.join(FIGURES_DIR,"gov_reinf_mk.pdf"), bbox_inches="tight")

fig_2, ax_2 = plot_moment_curvature(mk_conc_gov,  x = 0.5, title = f"C.1_3: Moment-curvature-diagram for concrete governing section \nnum_post_yield = {num_post_yield}")
fig_2.savefig(os.path.join(FIGURES_DIR,"gov_conc_mk.pdf"), bbox_inches="tight")

# strain profiles
fig_3, ax_3 = plot_strain_profile(mk_u_result_reinf_gov, title = f"C.2 : Strain profile at breaking point of section at x = 0.5 \nnum_post_yield = {num_post_yield}")
fig_3.savefig(os.path.join(FIGURES_DIR,"gov_reinf_sp.pdf"), bbox_inches="tight")

fig_4, ax_4 = plot_strain_profile(mk_u_result_conc_gov, title = f"C.1_3: Strain profile at breaking point of section at x = 0.5 \nnum_post_yield = {num_post_yield}")
fig_4.savefig(os.path.join(FIGURES_DIR,"gov_conc_sp.pdf"), bbox_inches="tight")

plt.show()