"""
Test file for deflection calculations
Author: Elliot Melcer
"""

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_3
from _mains.testing_files.testing_loads import test_loads

"""
Testing Load Combination Methods

passed: 02.02.2026

Output: 

Loads:
  Self-weight: 2.99 kN/m²
  Non-structural: 3.28 kN/m²
  Live load: 3.0 kN/m²

1. FUNDAMENTAL COMBINATION (ULS)
   q_fund: 12.96 kN/m²

2. QUASI-PERMANENT COMBINATION (SLS)
   q_qp: 7.17 kN/m²

3. FREQUENT COMBINATION (SLS)
   q_freq: 9.27 kN/m²
"""

slab = test_slab_construction_c1_3

# Load information
print(f"\nLoads:")
print(f"  Self-weight: {slab.structural_dead_load_kN_m2():.2f} kN/m²")
print(f"  Non-structural: {slab.non_structural_dead_load_kN_m2():.2f} kN/m²")
print(f"  Live load: {test_loads.Qk[0]:.1f} kN/m²")

# Fundamental combination (ULS)

print("\n1. FUNDAMENTAL COMBINATION (ULS)")
q_fund_kN_m2 = test_loads.fundamental_combination_kN_m2_EC0(slab)
print(f"   q_fund: {q_fund_kN_m2:.2f} kN/m²")

# Quasi-permanent combination (SLS - typical for long-term deflection checks)
print("\n2. QUASI-PERMANENT COMBINATION (SLS)")
q_qp_kN_m2 = test_loads.quasi_permanent_combination_kN_m2_EC0(slab)
print(f"   q_qp: {q_qp_kN_m2:.2f} kN/m²")

# Frequent combination (SLS - typical for short-term deflection checks)
print("\n3. FREQUENT COMBINATION (SLS)")
q_freq_kN_m2 = test_loads.frequent_combination_kN_m2_EC0(slab)
print(f"   q_freq: {q_freq_kN_m2:.2f} kN/m²")

# Frequent combination (SLS - typical for short-term deflection checks)
print("\n4. RARE COMBINATION (SLS)")
q_rare_kN_m2 = test_loads.rare_combination_kN_m2_EC0(slab)
print(f"   q_rare: {q_rare_kN_m2:.2f} kN/m²")
