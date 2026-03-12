from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_shell_c1_4_uls
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1, \
    test_slab_construction_c1_2_c50, test_slab_construction_c1_2_c80, test_slab_construction_c1_3
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm, calculate_prestress_moment_Nmm, \
    calculate_bending_strength_sls_Nmm, calculate_moment_curvature_sls
from core.visualization_core.visualization import plot_moment_curvature
from slab_construction.slab_construction import SlabConstruction

"""
Use the values from the print statement as input for the Grasshopper Function "M-Kappa V2" 
in Jamila's Grasshopper code to verify the deflection calculation

Methodology:
 1. Run this file
 2. Use Printout as input for the Grasshopper Function "M-Kappa V2" -> Grasshopper Result
 4. Run deflection_test.py file: -> Python Result
 5. Compare Results
 
Results: 
                   |    Grasshopper     |    Python*   |  Diff
=========|=========|====================|==============+=========
c1_1     | GZG/GZG |    8.559863 mm     |    8.08 mm   | - 5.5 %
         | GZT/GZG |   73.405091 mm     |   60.84 mm   | -17.1 %
---------+---------+--------------------+--------------|--------- 
c1_2_c50 | GZG/GZG |   -8.328817   mm   |   -8.38 mm   |   0.7 %
         | GZT/GZG |   -2.987402   mm   |   -3.14 mm   |   5.1 %
---------+---------+--------------------+--------------|---------    
c1_2c_80 | GZG/GZG |   -6.796638 mm     |   -6.90 mm   |   1.5 %
         | GZT/GZG |   -2.382132 mm     |   -2.63 mm   |  10.4 %
---------+---------+--------------------+--------------|--------- 
c1_3     | GZG/GZG |    4.590455 mm     |   13.66 mm   | 197.6 %
         | GZT/GZG |    17.613091mm     |   25.22 mm   |  43.2 %
---------+---------+--------------------+--------------|--------- 
c1_4     | GZG/GZG |   -8.392501 mm     |   -8.40 mm   |   0.1 %
         | GZT/GZG |   -6.437118 mm     |   -6.52 mm   |   1.2 %

*deflection_test.py
"""

# Verify Slab Construction
slab_construction = test_slab_construction_c1_1
#---------------------------------------------------

# Sections
hp_section_uls_mid     = slab_construction.slab.section_at(0.5)
hp_section_uls_supp     = slab_construction.slab.section_at(0.0)

# Loads
q_fund_kN_m2 = test_loads.fundamental_combination(slab_construction)
q_qp_kN_m2 = test_loads.quasi_permanent_combination(slab_construction)

# Cracking Moment
m_cr_res_mid = calculate_cracking_moment_sls_Nmm(hp_section_uls_mid)
m_cr_res_supp = calculate_cracking_moment_sls_Nmm(hp_section_uls_supp)

# Prestress Moment
m_p_mid = calculate_prestress_moment_Nmm(hp_section_uls_mid)
m_p_supp = calculate_prestress_moment_Nmm(hp_section_uls_supp)

# Ultimate Moment
m_u_mid = calculate_bending_strength_sls_Nmm(hp_section_uls_mid)
m_u_supp = calculate_bending_strength_sls_Nmm(hp_section_uls_supp)

# Cracking Curvature at Midspan
_, kappa_cr, _ = m_cr_res_mid.get("strain_profile", (None, None, None))


# Ultimate Curvature at Midspan
_, kappa_u, _ = m_u_mid.get("strain_profile", (None, None, None))

# Moment Curvature Diagram at Midspan
mk_res = calculate_moment_curvature_sls(hp_section_uls_mid)
plot_moment_curvature(mk_res, x = 0.5)

# Output

print(f"q_qp: {q_qp_kN_m2:.2f} kN/m²")
print(f"q_fund: {q_fund_kN_m2:.2f} kN/m²")

print(f"M_p Mid (SLS): {m_p_mid *10**(-6):.2f}")
print(f"M_p Support (SLS): {m_p_supp *10**(-6):.2f}")

print(f"M_cr Mid (SLS): {m_cr_res_mid.get("m_cr") *10**(-6):.2f}")
print(f"M_u Mid (SLS): {m_u_mid.get("m_u") * 10**(-6):.2f}")

print(f"M_cr Support (SLS): {m_cr_res_supp.get("m_cr") * 10**(-6):.2f}")
print(f"M_u Support (SLS): {m_u_supp.get("m_u") * 10**(-6):.2f}")

print(f"kappa_cr Mid (SLS): {kappa_cr * 1000}")
print(f"kappa_u Mid (SLS): {kappa_u * 1000}")

plt.show()