from matplotlib import pyplot as plt

from core.analysis_core import section_methods
from _mains.testing_files.testing_hp_sections import hp_section_c1_1_uls, hp_section_c1_2_c50_uls, \
    hp_section_c1_2_c80_uls, hp_section_c1_3_uls, hp_section_c1_4_uls
from core.analysis_core.section_methods import get_concrete, calculate_cracking_moment_sls, get_reinforcement
from core.visualization_core.visualization import plot_strain_profile, plot_constitutive_law_concrete, \
    plot_constitutive_law_reinforcement, plot_cross_section

"""
This file is used for verification of the cracking moment method. 

The sections used for verification are from chapter "C.1. Vergleich der Riss- und Bruchmomente" in Loutfi (2023)

passed 29.12.2025

Output:

Section     Mcr [kNm]
1               37.53
2 (C50/60)     185.10
2 (C80/90)     192.82
3               46.34
4              409.73
"""

# Section 1:

results_c1_1        = calculate_cracking_moment_sls(hp_section_c1_1_uls, n=0)
results_c1_2_c50    = calculate_cracking_moment_sls(hp_section_c1_2_c50_uls, n=0)
results_c1_2_c80    = calculate_cracking_moment_sls(hp_section_c1_2_c80_uls, n=0)
results_c1_3        = calculate_cracking_moment_sls(hp_section_c1_3_uls, n=0)
results_c1_4        = calculate_cracking_moment_sls(hp_section_c1_4_uls, n=0)

print(f"Cracking Moment Verification\n"
      f"\n"
      f"Section     Mcr [kNm]\n"
      f"1           {-results_c1_1.get("m_cr")      / 1e6:>9.2f}\n"
      f"2 (C50/60)  {-results_c1_2_c50.get("m_cr")  / 1e6:>9.2f}\n"
      f"2 (C80/90)  {-results_c1_2_c80.get("m_cr")  / 1e6:>9.2f}\n"
      f"3           {-results_c1_3.get("m_cr")      / 1e6:>9.2f}\n"
      f"4           {-results_c1_4.get("m_cr")      / 1e6:>9.2f}\n")

# Plots:

# --- cross-section ---
plot_cross_section(results_c1_1.get("section"), x = 0)
#
# #   - Constitutive Laws:
#
# plot_constitutive_law_concrete(get_concrete(results_c1_1.get("section")))
plot_constitutive_law_concrete(get_concrete(results_c1_1.get("section")))
# plot_constitutive_law_reinforcement(get_reinforcement(results_c1_1.get("section"))[0])
#
# #   - Section Strain Profile
plot_strain_profile(results_c1_1)
#
# # Display all plots
plt.show()

