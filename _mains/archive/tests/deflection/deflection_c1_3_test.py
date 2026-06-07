"""
Test file for deflection calculation
- Slab construction: test_slab_construction_c1_3

Conclusions:
 - MKLine for non-prestressed section nearly linear, when fctm = 0 (see two plots)
    - confirmed by inca2 M-K Data for the same cross-section fctm =/= 0 vs. fctm = 0
 - Python deflection is accurate
 - higher deflection comes from higher curvature under same load
 - the assumption that fctm = 0 in the entire cross-section is very conservative
"""
from matplotlib import pyplot as plt

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_3
from _mains.testing_files.testing_loads import test_loads
from core.analysis_core.section_methods import calculate_moment_curvature_sls_EC
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator
from core.visualization_core.visualization import plot_moment_curvature, plot_moment_curvature_with_reference

# ---------------------------------------------------------------------------
# Slab info
# ---------------------------------------------------------------------------
span_m = test_slab_construction_c1_3.slab.L / 1000  # mm → m

print("=" * 70)
print("DEFLECTION TEST — C1_3 | QUASI_PERMANENT | SIMPLE_BEAM")
print("=" * 70)

print(f"\nLoads:")
print(f"  Non-structural DL:   {test_slab_construction_c1_3.non_structural_dead_load_kN_m2():.2f} kN/m²")

# ---------------------------------------------------------------------------
# M-κ diagram points (support x=0.0 and midspan x=0.5)
# ---------------------------------------------------------------------------
def print_mk_points(label: str, x_norm: float) -> None:
    section = test_slab_construction_c1_3.slab.section_at(x_norm)
    mk_result = calculate_moment_curvature_sls_EC(
        section,
        n=0,
        constitutive_law="NONE_PARABOLIC"
    )
    M_list     = list(-mk_result.m_y / 1e6)       # Nmm → kNm, positive sagging
    kappa_list = list(-mk_result.chi_y * 1000)     # 1/mm → 1/m, positive sagging

    print(f"\n  M     [kNm] = {[round(v, 4) for v in M_list]}")
    print(f"  kappa [1/m] = {[round(v, 6) for v in kappa_list]}")
#
# print(f"\n" + "=" * 70)
# print("M-κ DIAGRAM POINTS")
# print("=" * 70)
#
# print(f"\n--- Support (x = 0.0) ---")
# print_mk_points("Support", 0.0)
#
print(f"\n--- Midspan (x = 0.5) ---")
print_mk_points("Midspan", 0.5)

mk_results = calculate_moment_curvature_sls_EC(test_slab_construction_c1_3.slab.section_at(0.5), constitutive_law="NONE_PARABOLIC")

#----------------------------------------------------------------------------
# Results from INCA
#----------------------------------------------------------------------------

inca_curvatures_fctm_not_0 = [0.0, 0.0000958, 0.0001916, 0.0002875, 0.0003833, 0.0004791, 0.0005749, 0.0006707, 0.0007665, 0.0008624, 0.0009582, 0.0010540, 0.0012456, 0.0014373, 0.0017247, 0.0022038, 0.0029703, 0.0043118, 0.0068988, 0.0070905, 0.0094859, 0.0117855, 0.0138935, 0.0157140, 0.0172471, 0.0183969, 0.0191635]
inca_moments_fctm_not_0 = [-0.0, 8.6590, 16.9183, 24.6943, 31.8488, 38.0857, 42.7710, 46.4243, 49.5323, 52.2852, 54.7895, 57.1114, 61.3710, 65.2828, 70.7426, 79.2120, 91.9488, 113.2415, 153.0375, 156.1622, 206.8669, 254.0079, 295.3490, 328.9220, 354.8301, 372.0099, 381.7650]

inca_curvatures_fctm_0 = [0.0000e-3, 0.4791e-3, 1.7247e-3, 3.5452e-3, 5.7489e-3, 8.1443e-3, 10.5396e-3, 12.7434e-3, 14.6597e-3, 16.2885e-3, 17.6299e-3, 18.7797e-3, 19.1630e-3]
inca_moments_fctm_0 = [0.0000, 10.7612, 38.6209, 78.9944, 127.2226, 178.6449, 228.6961, 273.0707, 309.7851, 338.9578, 360.8323, 377.1116, 381.7743]
# ---------------------------------------------------------------------------
# Deflection calculation
# ---------------------------------------------------------------------------
print(f"\n" + "=" * 70)
print("DEFLECTION RESULT")
print("=" * 70)

deflection = DeflectionCalculator.calculate_deflection_mm_EC(
    test_slab_construction_c1_3,
    test_loads,
    system=SystemType.SIMPLE_BEAM,
    combination="QUASI_PERMANENT",
    debug=True
)

print(f"\n  Deflection:        {deflection:.2f} mm")

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

plot_moment_curvature_with_reference(mk_results, inca_curvatures_fctm_not_0, inca_moments_fctm_not_0, title="INCA2: fctm =/= 0\nPython fctm = 0")

plot_moment_curvature_with_reference(mk_results, inca_curvatures_fctm_0, inca_moments_fctm_0, title="INCA2: fctm = 0\nPython fctm = 0")

plt.show()