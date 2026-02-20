from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_2_c50, \
    test_slab_construction_c1_4, test_slab_construction_c1_3

"""
Testing infill_area_density_kg_m2() method

Results:

Config | kg/m² Python | kg/m² GH
-------+--------------+-----------
c1_1   |    99.09     |   99.09
c1_2   |   184.81     |  184.81
c1_3   |   343.84     |  343.84
c1_4   |   237.70     |  237.70 

passed: 20.02.2026
"""

infill_area_density_kg_m2_c1_1 = test_slab_construction_c1_1.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_2 = test_slab_construction_c1_2_c50.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_3 = test_slab_construction_c1_3.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_4 = test_slab_construction_c1_4.infill_area_density_kg_m2()

print("Testing infill_area_density_kg_m2() method \n")
print(f"c1_1 : {infill_area_density_kg_m2_c1_1:.2f} kg/m²")
print(f"c1_2 : {infill_area_density_kg_m2_c1_2:.2f} kg/m²")
print(f"c1_3 : {infill_area_density_kg_m2_c1_3:.2f} kg/m²")
print(f"c1_4 : {infill_area_density_kg_m2_c1_4:.2f} kg/m²")