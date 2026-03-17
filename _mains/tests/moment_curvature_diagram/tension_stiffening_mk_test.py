from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_4_uls, hp_section_c1_3_uls, hp_shell_c1_3_uls
from core.analysis_core.section_methods import sls_section, get_concrete, calculate_moment_curvature_sls, \
    calculate_cracking_moment_sls_Nmm
from core.visualization_core.visualization import plot_constitutive_law_concrete, plot_moment_curvature, \
    plot_moment_curvature_with_reference

section_mid = hp_shell_c1_3_uls.section_at(0.5)
section_sup = hp_shell_c1_3_uls.section_at(0)

sls_section_tension_nocracking_mid = sls_section(section_mid, concrete_tension=True, cracking = False)
sls_section_tension_cracking_mid   = sls_section(section_mid, concrete_tension=True, cracking = True)
sls_section_notension_mid          = sls_section(section_mid, concrete_tension=False)

mk_tension_nocracking_mid = calculate_moment_curvature_sls(section_mid, concrete_tension=True, cracking = False)
mk_tension_cracking_mid   = calculate_moment_curvature_sls(section_mid, concrete_tension=True, cracking = True)
mk_tension_cracking_sup   = calculate_moment_curvature_sls(section_sup, concrete_tension=True, cracking = True)
mk_notension_mid          = calculate_moment_curvature_sls(section_mid, concrete_tension=False)

# print("Mid")
print(mk_tension_cracking_mid.m_y)
print(mk_tension_cracking_mid.chi_y)

print("Support")
print(mk_tension_cracking_sup.m_y)
print(mk_tension_cracking_sup.chi_y)

plot_constitutive_law_concrete(get_concrete(sls_section_tension_nocracking_mid))
plot_constitutive_law_concrete(get_concrete(sls_section_tension_cracking_mid))
plot_constitutive_law_concrete(get_concrete(sls_section_notension_mid))

m_cr = calculate_cracking_moment_sls_Nmm(section_mid)["m_cr"]
m_cr_mod = m_cr/ (-1e6)
strain_profile_cr = calculate_cracking_moment_sls_Nmm(section_mid)["strain_profile"]
_, kappa_cr, _ = strain_profile_cr
kappa_cr_mod = kappa_cr * (-1e3)
#
plot_moment_curvature_with_reference(mk_tension_nocracking_mid, [kappa_cr_mod], [m_cr_mod], x = 0.5, title = "mk_tension_nocracking")
plot_moment_curvature_with_reference(mk_tension_cracking_mid,   [kappa_cr_mod], [m_cr_mod], x = 0.5, title = "mk_tension_cracking")
plot_moment_curvature_with_reference(mk_notension_mid,          [kappa_cr_mod], [m_cr_mod], x = 0.5, title = "mk_notension")

plt.show()