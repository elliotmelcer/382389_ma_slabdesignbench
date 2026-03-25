from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_4_uls
from core.analysis_core.section_methods import calculate_moment_curvature_sls, calculate_cracking_moment_sls_Nmm
from core.visualization_core.visualization import plot_moment_curvature

test_section = hp_section_c1_4_uls

# M-K Results for a concrete with fctm = 0
cracked_m_k_results = calculate_moment_curvature_sls(
    test_section,
    constitutive_law="NONE_PARABOLIC"
)

# M-K Results for a concrete with fctm != 0
uncracked_m_k_results = calculate_moment_curvature_sls(
    test_section,
    constitutive_law="FCTM_PARABOLIC"
)

mcr = calculate_cracking_moment_sls_Nmm(
    test_section,
)

print("mcr = ", mcr["m_cr"])

plot_moment_curvature(cracked_m_k_results, title = "fctm = 0")
plot_moment_curvature(uncracked_m_k_results, title = "fctm != 0")

plt.show()