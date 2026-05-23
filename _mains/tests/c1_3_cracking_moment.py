import numpy as np
from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_3_uls, hp_shell_c1_3_uls, hp_shell_c2_uls
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm_EC, calculate_moment_curvature_sls_EC, \
    get_concrete, sls_section_EC
from core.visualization_core.visualization import plot_moment_curvature, PlotLine, plot_moment_curvature_multiple, \
    plot_strain_profile

"""
This file was written to see if the mcr from calculate_moment_curvature_sls_EC is equal to the moment on the mk-line where the curvature is the same as under Mcr from calculate_moment_curvature_sls_EC.

Result: it is indeed the same. as a result the function _full_moment_curvature_method was changed
"""

x = 0.5

section = hp_section_c1_3_uls
sls_section = sls_section_EC(section, constitutive_law="FCTM_PARABOLIC")

concrete = get_concrete(section)
Ecm = concrete.Ecm
f_ctm = concrete.fctm
eps_ctm = f_ctm/Ecm
print("eps_ctm = ", eps_ctm)

# moment curvature
m_k_x = calculate_moment_curvature_sls_EC(section, constitutive_law="FCTM_PARABOLIC")

# cracking
M_cr_x = calculate_cracking_moment_sls_Nmm_EC(section)["m_cr"]
sp = sls_section.section_calculator.calculate_strain_profile(0, M_cr_x, 0)
_, kappa_cr, _ = sp
sp_result = {
    "section": section,
    "strain_profile": sp,
}
plot_strain_profile(sp_result)


m_cr_list = []
xs = np.linspace(0, 0.5, 41)
for _x in xs:
    _section = hp_shell_c1_3_uls.section_at(_x)
    _m_cr = calculate_cracking_moment_sls_Nmm_EC(_section)["m_cr"]
    m_cr_list.append(_m_cr)

# mcr_line = PlotLine(m_cr_list, xs.tolist(), "M_cr")
# lines  =[mcr_line]

# plot_moment_curvature_multiple(lines, xmarker=1_000_000, ymarker=1_000_000)

m_k_x_kappa_cr = sls_section.section_calculator.calculate_moment_curvature(chi=[kappa_cr])
mcr_m_k_x = m_k_x_kappa_cr.m_y[0]

plot_moment_curvature(m_k_x)
print(f"Mcr at {x} (from direct calculation): {M_cr_x}")
print(f"Mcr at {x} (from MKD): {mcr_m_k_x}")
plt.show()

