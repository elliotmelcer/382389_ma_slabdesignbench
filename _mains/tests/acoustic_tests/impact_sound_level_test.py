from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_3, \
    test_slab_construction_c1_4, test_slab_construction_c1_2_c50, test_slab_construction_ref
from core.analysis_core.acoustic_methods import  calculate_standard_impact_sound_pressure_level

"""
Testing Calculation of Impact Sound Level

Results for L'_nw:

Config   | Util Python |  Util GH
---------+-------------+-----------
c1_1     |    66.62    |    67.35
c1_2     |    62.50    |    63.24
c1_3     |    63.06    |    63.79
c1_4     |    56.18    |    56.74     
ref      |    60.44    |    61.17  

Difference comes from way Ecm is calculated: Ecm = 22000(fcm/10)**0.3. 
The GH Script uses the values for Ecm from Schneider Bautabellen rounded to the next 1000

eg. C55/67: Ecm = 22000(63/10)**0.3 = 38214 N/mm², in GH rounded to 38000 N/mm² 

passed: 20.02.2026
"""

print("Testing Calculation of Sound Reduction Index R_w")

L_nw_c1_1 = calculate_standard_impact_sound_pressure_level(test_slab_construction_c1_1,     0.01)
L_nw_c1_2 = calculate_standard_impact_sound_pressure_level(test_slab_construction_c1_2_c50, 0.01)
L_nw_c1_3 = calculate_standard_impact_sound_pressure_level(test_slab_construction_c1_3,     0.01)
L_nw_c1_4 = calculate_standard_impact_sound_pressure_level(test_slab_construction_c1_4,     0.01)
L_nw_ref  = calculate_standard_impact_sound_pressure_level(test_slab_construction_ref,      0.01)

print(f"L_nw_c1_1: {L_nw_c1_1:.2f}")
print(f"L_nw_c1_2: {L_nw_c1_2:.2f}")
print(f"L_nw_c1_3: {L_nw_c1_3:.2f}")
print(f"L_nw_c1_4: {L_nw_c1_4:.2f}")
print(f"L_nw_ref:  {L_nw_ref:.2f}")