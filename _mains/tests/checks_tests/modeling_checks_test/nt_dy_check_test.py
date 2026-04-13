"""
Testing of Z.1 nt and dy Combinations

Results:

Configuration | Util Python | Util GH
--------------+-------------+---------
 dy=50,  nt=1 |    10.0     |   10.0
 dy=300, nt=1 |    1.0      |   1.0
 dy=300, nt=2 |    1.0      |   1.0
 dy=50,  nt=2 |    1.0      |   1.0

passed: 19.02.2026
"""
from _mains.testing_files.testing_floor import test_floor
from _mains.testing_files.testing_materials import concrete_c50_uls, solidian_Q95_pre_20, infill
from core.analysis_core.checks.modeling_checks import NtDyCombinationCheck
from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.hp_model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.hp_model.hp_slab import HPSlab

# Base geometry parameters (fixed, according to hp_c1_1)
BASE_PARAMS = dict(
    B=1200,
    L=6750,
    Hx=40,
    Hy=160,
    t=40,
)

print("Testing of Z.1 nt and dy Combinations\n")

def make_test_slab_construction_c1_1(base_params: dict, dy: float, nt: int) -> SlabConstruction:
    hp_geom = HPGeometry(**base_params, dy=dy, nt=nt)
    hp_shell = HPShell(hp_geom, concrete_c50_uls, solidian_Q95_pre_20, reinf_area=50)
    hp_slab = HPSlab(hp_shell, infill)
    slab_construction = SlabConstruction(hp_slab, test_floor)
    return slab_construction

# --- CASE 1 ---
# nt == 1 AND abs(dy - dy_real) > 0.01 -> utilization = 1.0
test_sc_1_50 = make_test_slab_construction_c1_1(BASE_PARAMS, dy=50, nt=1)
util_1_50 = NtDyCombinationCheck.calculateUtilization(test_sc_1_50)
print("Case 1 (nt=1, dy=50)")
print("util = ", util_1_50, "\n")


# --- CASE 2 ---
# nt == 1 AND abs(dy - dy_real) < 0.01 -> utilization = 10.0
test_sc_1_300 = make_test_slab_construction_c1_1(BASE_PARAMS, dy=300, nt=1)
util_1_300 = NtDyCombinationCheck.calculateUtilization(test_sc_1_300)
print("Case 2 (nt=1, dy=300)")
print("util = ", util_1_300, "\n")

# --- CASE 3 ---
# nt != 1 AND dy matches -> utilization = 1.0
test_sc_2_300 = make_test_slab_construction_c1_1(BASE_PARAMS, dy=300, nt=2)
util_2_300 = NtDyCombinationCheck.calculateUtilization(test_sc_2_300)
print("Case 3 (nt=2, dy=300)")
print("util = ", util_2_300, "\n")

# --- CASE 4 ---
# nt != 1 AND dy differs significantly -> still utilization = 1.0
test_sc_2_50 = make_test_slab_construction_c1_1(BASE_PARAMS, dy=50, nt=2)
util_2_50 = NtDyCombinationCheck.calculateUtilization(test_sc_2_50)
print("Case 4 (nt=2, dy=50)")
print("util = ", util_2_50, "\n")




