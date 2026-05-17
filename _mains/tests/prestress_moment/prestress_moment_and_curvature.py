import numpy as np
from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_4_uls
from core.analysis_core.section_methods import sls_section, calculate_prestress_forces_Nmm, \
    calculate_cracking_moment_sls_Nmm, calculate_moment_curvature_sls
from core.visualization_core.visualization import plot_moment_curvature_with_reference, plot_moment_curvature

section = hp_section_c1_4_uls
sls_section = sls_section(section, "TENSTIFF_PARABOLIC")

M_p, N_p = calculate_prestress_forces_Nmm(section)
M_p_sls, N_p_sls = calculate_prestress_forces_Nmm(sls_section)

#
# ----------------------------------------------------------------------------------------------------------
#

"""Moment- Curvature Diagram"""
mk_res = calculate_moment_curvature_sls(section)
plot_moment_curvature(mk_res)

#
# ----------------------------------------------------------------------------------------------------------
#

print("\n")
print("Difference between prestress moment of section and sls_section")
print("**************************************************************")
print(f"calculate_prestress_moment_Nmm(section):     {M_p}")
print(f"calculate_prestress_moment_Nmm(sls_section): {M_p_sls}")

#
# ----------------------------------------------------------------------------------------------------------
#


print("\n")
print("Different Kappa_0 Calculations")
print("**************************************************************")

"""Direct Calculation"""
_, kappa_0_direct, _ = sls_section.section_calculator.calculate_strain_profile(-N_p_sls, -M_p_sls, 0)
print(f"N_p_sls = {N_p_sls}")
print(f"M_p_sls = {M_p_sls}")
print(f"kappa_0_direct: {kappa_0_direct}")





"""Indirect Calculation"""
results = sls_section.section_calculator.calculate_moment_curvature(
    n=0,
    num_pre_yield=40,
    num_post_yield=0  # in case concrete is governing, at least 1 post yield point is necessary
)

kappa_0_indirect = 0.0

# Get tension_stiffening properties (using same material model)
M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=0)

# Determine initial curvature from prestressing kappa_0

# Method 1: Use M_cr and kappa_cr
M_cr = abs(M_cr_result["m_cr"])  # Nmm
kappa_cr = abs(M_cr_result["strain_profile"][1])  # 1/mm
if abs(M_cr - M_p) > 1e-3:
    kappa_0_indirect_m1 = (M_p * kappa_cr) / (M_cr - M_p)
else:
    kappa_0_indirect_m1 = 0.0

# Method 2 fallback: Use initial slope of M-κ curve
if len(results.chi_y) >= 5:
    slope, intercept = np.polyfit(results.chi_y[:2], results.m_y[:2], 1)
    kappa_0_indirect_m2 = -intercept / slope if slope > 1e-6 else 0.0
else:
    kappa_0_indirect_m2 = 0.0

print(f"kappa_0_indirect Method 1: {kappa_0_indirect_m1}")
print(f"kappa_0_indirect Method 2: {kappa_0_indirect_m2}")

# -----------------------------------------------------------------------------------------------------
plt.show()