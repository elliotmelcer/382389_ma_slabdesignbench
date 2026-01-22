from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_1_uls, hp_section_c1_2_c50_uls, \
    hp_section_c1_2_c80_uls, hp_section_c1_3_uls, hp_section_c1_4_uls
from core.analysis_core.section_methods import calculate_bending_strength_uls, get_concrete
from core.unit_core import Nmm_to_kNm
from core.visualization_core.visualization import plot_cross_section, plot_constitutive_law_concrete, \
    plot_strain_profile

"""
This file is used for verification of the cracking moment method. 

The sections used for verification are from chapter "C.1. Vergleich der Riss- und Bruchmomente" in Loutfi (2023)

passed 29.12.2025

Output:

Section     Mu [kNm]
1               53.79
2 (C50/60)     212.51
2 (C80/90)     240.86
3              251.38
4              490.12
"""

# Section 1:

results_c1_1        = calculate_bending_strength_uls(hp_section_c1_1_uls)
results_c1_2_c50    = calculate_bending_strength_uls(hp_section_c1_2_c50_uls)
results_c1_2_c80    = calculate_bending_strength_uls(hp_section_c1_2_c80_uls)
results_c1_3        = calculate_bending_strength_uls(hp_section_c1_3_uls)
results_c1_4        = calculate_bending_strength_uls(hp_section_c1_4_uls)

print(f"Ultimate Moment (ULS) Verification\n"
      f"\n"
      f"Section     Mu [kNm]\n"
      f"1           {Nmm_to_kNm(-results_c1_1.get('m_u'))       :>9.2f}\n"
      f"2 (C50/60)  {Nmm_to_kNm(-results_c1_2_c50.get('m_u'))   :>9.2f}\n"
      f"2 (C80/90)  {Nmm_to_kNm(-results_c1_2_c80.get('m_u'))   :>9.2f}\n"
      f"3           {Nmm_to_kNm(-results_c1_3.get('m_u'))       :>9.2f}\n"
      f"4           {Nmm_to_kNm(-results_c1_4.get('m_u'))       :>9.2f}\n")

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