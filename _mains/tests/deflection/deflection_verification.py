from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_shell_c1_4_uls
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm, calculate_prestress_moment_Nmm, \
    calculate_bending_strength_sls_Nmm, calculate_moment_curvature_sls
from core.visualization_core.visualization import plot_moment_curvature

"""
Use the values from the print statement as input for the Grasshopper Function "M-Kappa V2" 
in Jamila's Grasshopper code to verify the deflection calculation

Result: 
c1_4    |    Grasshopper     |    Python*   
--------+--------------------+--------------
GZG/GZG |   -8.392507 mm     |   -8.40 mm   
GZT/GZG |   -6.427123 mm     |   -6.52 mm   

*deflection_test.py
"""

slab_construction = test_slab_construction_c1_4

# Sections
hp_section_c1_4_uls_mid     = slab_construction.slab.section_at(0.5)
hp_section_c1_4_uls_supp     = slab_construction.slab.section_at(0.0)

# Loads
q_fund_kN_m2 = test_loads.fundamental_combination(slab_construction)
q_qp_kN_m2 = test_loads.quasi_permanent_combination(slab_construction)

# Cracking Moment
m_cr_res_mid = calculate_cracking_moment_sls_Nmm(hp_section_c1_4_uls_mid)
m_cr_res_supp = calculate_cracking_moment_sls_Nmm(hp_section_c1_4_uls_supp)

# Prestress Moment
m_p_mid = calculate_prestress_moment_Nmm(hp_section_c1_4_uls_mid)
m_p_supp = calculate_prestress_moment_Nmm(hp_section_c1_4_uls_supp)

# Ultimate Moment
m_u_mid = calculate_bending_strength_sls_Nmm(hp_section_c1_4_uls_mid)
m_u_supp = calculate_bending_strength_sls_Nmm(hp_section_c1_4_uls_supp)

# Cracking Curvature at Midspan
_, kappa_cr, _ = m_cr_res_mid.get("strain_profile", (None, None, None))


# Ultimate Curvature at Midspan
mk_res = calculate_moment_curvature_sls(hp_section_c1_4_uls_mid)
plot_moment_curvature(mk_res, x = 0.5)

kappa_u = float(mk_res.chi_y[-1])



# Output

print(f"q_fund: {q_fund_kN_m2:.2f} kN/m²")
print(f"q_qp: {q_qp_kN_m2:.2f} kN/m²")

print(f"Prestress Mid: {m_p_mid *10**(-6):.2f}")
print(f"Prestress Support: {m_p_supp *10**(-6):.2f}")

print(f"Cracking Mid: {m_cr_res_mid.get("m_cr") *10**(-6):.2f}")
print(f"Ultimate Mid: {m_u_mid.get("m_u") * 10**(-6):.2f}")

print(f"Cracking Support: {m_cr_res_supp.get("m_cr") * 10**(-6):.2f}")
print(f"Ultimate Support: {m_u_supp.get("m_u") * 10**(-6):.2f}")

print(f"kappa_cr Mid: {kappa_cr * 1000}")
print(f"kappa_u Mid: {kappa_u * 1000}")

plt.show()