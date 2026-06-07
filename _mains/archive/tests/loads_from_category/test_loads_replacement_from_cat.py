from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_3
from core.analysis_core.statics.loads import LoadsEC

"""
Confirms I can use B2 instead of manual test_loads:

live_loads = [3.0] #kN/m²

psi_0_values = [1.0]
psi_1_values = [1.0]
psi_2_values = [0.3]

Only difference is in the frequent combination, but that one is not used in my calculations

Results (24.05.26):

===============================================
test_loads:
===============================================
fundamental combination:        12.38 kN/m²
rare combination:               8.84 kN/m²
quasi-permanent combination:    6.74 kN/m²
frequent:                       8.84 kN/m²

===============================================
from categories: ['B2']
===============================================
fundamental combination:        12.38 kN/m²
rare combination:               8.84 kN/m²
quasi-permanent combination:    6.74 kN/m²
frequent:                       7.34 kN/m²

Process finished with exit code 0
"""

slab_con = test_slab_construction_c1_3

# test_loads
test_fc = test_loads.fundamental_combination_kN_m2_EC0(slab_con)
test_rc = test_loads.rare_combination_kN_m2_EC0(slab_con)
test_qp = test_loads.quasi_permanent_combination_kN_m2_EC0(slab_con)
test_fr = test_loads.frequent_combination_kN_m2_EC0(slab_con)

# from category
cat = ["B2"]
loads_from_cat = LoadsEC.from_categories_EC0_NA_DE(cat)

lfc_fc = loads_from_cat.fundamental_combination_kN_m2_EC0(slab_con)
lfc_rc = loads_from_cat.rare_combination_kN_m2_EC0(slab_con)
lfc_qp = loads_from_cat.quasi_permanent_combination_kN_m2_EC0(slab_con)
lfc_fr = loads_from_cat.frequent_combination_kN_m2_EC0(slab_con)

# Print outs
print("===============================================")
print("test_loads:")
print("===============================================")
print(f"fundamental combination:        {test_fc:.2f} kN/m²")
print(f"rare combination:               {test_rc:.2f} kN/m²")
print(f"quasi-permanent combination:    {test_qp:.2f} kN/m²")
print(f"frequent:                       {test_fr:.2f} kN/m²")

print("")

print("===============================================")
print(f"from categories: {cat}")
print("===============================================")
print(f"fundamental combination:        {lfc_fc:.2f} kN/m²")
print(f"rare combination:               {lfc_rc:.2f} kN/m²")
print(f"quasi-permanent combination:    {lfc_qp:.2f} kN/m²")
print(f"frequent:                       {lfc_fr:.2f} kN/m²")