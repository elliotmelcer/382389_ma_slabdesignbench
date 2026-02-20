from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_1, test_slab_construction_c1_3, \
    test_slab_construction_c1_4, test_slab_construction_c1_2_c50
from core.analysis_core.acoustic_meethods import calculate_sound_reduction_index

"""
Testing Calculation of Sound Reduction Index R_w

Results for R_w:

Config   | Util Python | Util Python | Util GH
---------+-------------+-------------+----------
m_conc = |   rho * t   | rho * V / A | rho * t 
---------+-------------+-------------+----------
c1_1     |    56.29    |    56.32    |   56.29
c1_2     |    56.75    |    56.81    |   56.75
c1_3     |    57.24    |    57.28    |   57.24
c1_4     |    56.78    |    56.85    |   56.78       

passed: 20.02.2026
"""

print("Testing Calculation of Sound Reduction Index R_w")

R_w_c1_1 = calculate_sound_reduction_index(test_slab_construction_c1_1,     0.01)
R_w_c1_2 = calculate_sound_reduction_index(test_slab_construction_c1_2_c50, 0.01)
R_w_c1_3 = calculate_sound_reduction_index(test_slab_construction_c1_3,     0.01)
R_w_c1_4 = calculate_sound_reduction_index(test_slab_construction_c1_4,     0.01)

print(f"R_1_c1_1: {R_w_c1_1:.2f}")
print(f"R_1_c1_2: {R_w_c1_2:.2f}")
print(f"R_1_c1_3: {R_w_c1_3:.2f}")
print(f"R_1_c1_4: {R_w_c1_4:.2f}")