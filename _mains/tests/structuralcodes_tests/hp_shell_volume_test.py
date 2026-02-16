from _mains.testing_files.testing_hp_sections import hp_c1_1, hp_c1_2, hp_c1_3, hp_c1_4

"""
Test to Verify the Calculation of the HP_Shell Volume

passed 23.12.2025

hp_c1_1 Volume: 0.338795 m³
hp_c1_2 Volume: 0.651013 m³
hp_c1_3 Volume: 0.631016 m³
hp_c1_4 Volume: 1.009294 m³
"""

print(f"hp_c1_1 Volume: {hp_c1_1.volume / 10e8:.6f} m³")
print(f"hp_c1_2 Volume: {hp_c1_2.volume / 10e8:.6f} m³")
print(f"hp_c1_3 Volume: {hp_c1_3.volume / 10e8:.6f} m³")
print(f"hp_c1_4 Volume: {hp_c1_4.volume / 10e8:.6f} m³")

