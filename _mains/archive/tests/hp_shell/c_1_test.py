from _mains.testing_files.testing_hp_sections import hp_shell_c1_1_uls, hp_shell_c1_2_c50_uls, hp_shell_c1_3_uls, \
    hp_shell_c1_4_uls

print("c_1_concrete_cover():\n")
print("hp_shell_c_1: ", hp_shell_c1_1_uls.c_1_clear_concrete_cover())
print("hp_shell_c_2: ", hp_shell_c1_2_c50_uls.c_1_clear_concrete_cover())
print("hp_shell_c_3: ", hp_shell_c1_3_uls.c_1_clear_concrete_cover())
print("hp_shell_c_4: ", hp_shell_c1_4_uls.c_1_clear_concrete_cover())