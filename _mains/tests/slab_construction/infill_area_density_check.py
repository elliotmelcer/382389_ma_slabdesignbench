from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_2_c50, \
    test_slab_construction_c1_4, test_slab_construction_c1_3

infill_area_density_kg_m2_c1_1 = test_slab_construction_c1_1.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_2 = test_slab_construction_c1_2_c50.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_3 = test_slab_construction_c1_3.infill_area_density_kg_m2()
infill_area_density_kg_m2_c1_4 = test_slab_construction_c1_4.infill_area_density_kg_m2()

print("infill area density test \n")
print(f"c1_1 : {infill_area_density_kg_m2_c1_1:.2f} kg/m²")
print(f"c1_2 : {infill_area_density_kg_m2_c1_2:.2f} kg/m²")
print(f"c1_3 : {infill_area_density_kg_m2_c1_3:.2f} kg/m²")
print(f"c1_4 : {infill_area_density_kg_m2_c1_4:.2f} kg/m²")