from _mains.testing_files.testing_hp_sections import hp_shell_c1_4_uls
from _mains.testing_files.testing_materials import infill
from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab

hp_slab_c1_4_uls = HPSlab(hp_shell_c1_4_uls, infill)

if __name__ == "__main__":
    print("self load = ", hp_slab_c1_4_uls.self_load())