from matplotlib import pyplot as plt
from structuralcodes.geometry import SurfaceGeometry
from structuralcodes.sections import GenericSection

from core.analysis_core import section_methods
from _mains.testing_files.testing_hp_sections import hp_section_c1_3_sls
from core.analysis_core.section_methods import get_concrete
from core.visualization_core.visualization import plot_strain_profile

"""
This file is used for verification of the cracking moment method. 

The sections used for verification are from chapter "C.1. Vergleich der Riss- und Bruchmomente" in Loutfi (2023)
"""

# Section 1:

results_c1_3        = section_methods.calculate_cracking_moment_sls(hp_section_c1_3_sls, n=0)


print(f"Cracking Moment Verification\n"
      f"\n"
      f"Section     Mcr [kNm]\n"
      f"3           {-results_c1_3.get("m_cr")  / 1e6:>9.2f}\n"
      )


# #   - Section Strain Profile
plot_strain_profile(hp_section_c1_3_sls, results_c1_3)
plt.show()

