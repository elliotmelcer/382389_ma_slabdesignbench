from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import (
    test_slab_construction_c1_1,
    test_slab_construction_c1_2_c50,
    test_slab_construction_c1_2_c80,
    test_slab_construction_c1_3,
    test_slab_construction_c1_4,
)
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator

"""
Output (25.03.2026):
c1_1:
  Deflection (QP) simplified: 8.249 mm
  Deflection (QP) full:       8.109 mm

c1_2_c50:
  Deflection (QP) simplified: -8.648 mm
  Deflection (QP) full:       -8.671 mm

c1_2_c80:
  Deflection (QP) simplified: -7.303 mm
  Deflection (QP) full:       -7.310 mm

c1_3:
  Deflection (QP) simplified: 5.103 mm
  Deflection (QP) full:       3.518 mm

c1_4:
  Deflection (QP) simplified: -8.967 mm
  Deflection (QP) full:       -8.994 mm
  
Conclusions:
 - Difference is largest, when section is not prestressed 
 
Ideas: 
 - include more points if section is not prestressed
 - Study with different amounts of prestress

"""

test_slabs = {
    "c1_1":     test_slab_construction_c1_1,
    "c1_2_c50": test_slab_construction_c1_2_c50,
    "c1_2_c80": test_slab_construction_c1_2_c80,
    "c1_3":     test_slab_construction_c1_3,
    "c1_4":     test_slab_construction_c1_4,
}


for name, slab_construction in test_slabs.items():
    deflection_qp_simple_mm = DeflectionCalculator.calculate_deflection_mm_EC(
        slab_construction   = slab_construction,
        loads               = test_loads,
        system              = SystemType.SIMPLE_BEAM,
        combination         = "QUASI_PERMANENT",
        n_intervals         = 40,
        N_axial_N           = 0.0,
        constitutive_law    = "TENSTIFF_PARABOLIC",
        load_history_method = "NONE",
        m_k_simplification  = 0.2,
        debug               = False,
    )

    deflection_qp_full_mm = DeflectionCalculator.calculate_deflection_mm_EC(
        slab_construction   = slab_construction,
        loads               = test_loads,
        system              = SystemType.SIMPLE_BEAM,
        combination         = "QUASI_PERMANENT",
        n_intervals         = 40,
        N_axial_N           = 0.0,
        constitutive_law    = "TENSTIFF_PARABOLIC",
        load_history_method = "NONE",
        m_k_simplification  = False,
        debug               = False,
    )

    print(f"{name}:")
    print(f"  Deflection (QP) simplified: {deflection_qp_simple_mm:.3f} mm")
    print(f"  Deflection (QP) full:       {deflection_qp_full_mm:.3f} mm")
    print()