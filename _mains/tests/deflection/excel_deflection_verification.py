from matplotlib import pyplot as plt

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_3
from _mains.testing_files.testing_loads import test_loads
from core.analysis_core.section_methods import calculate_moment_curvature_sls
from core.analysis_core.statics import calculate_line_load
from core.analysis_core.statics.deformations import DeflectionCalculator
from core.visualization_core.visualization import plot_moment_curvature, plot_moment_curvature_with_reference

"""
This file is used to analyze the deflection of test_slab_construction_c1_3 after finding large discrepancies between the 
Grasshopper and Python results in deflection_verification.py:

12.03.2026:        |    Grasshopper     |    Python*   |  Diff
=========|=========|====================|==============+=========
c1_3     | GZG/GZG |    4.590455 mm     |   13.66 mm   | 197.6 %
         | GZT/GZG |    17.613091mm     |   25.22 mm   |  43.2 %

The console output of this file is used for verification purposed in Verfizierung_Verformung_c1_3.xlsx

Conclusions from Verfizierung_Verformung_c1_3.xlsx:
 - the assumption that fctm = 0 in the entire cross-section is very conservative 
 - for the non-prestressed section this results in a much larger discrepancy from Jamilas deflection
 
Conclusions from https://concrete.ethz.ch/apps/sbe-ii/biegetragverhalten-vorspannung/:
 - the more prestress on a section, the smaller the difference between the bilinear Mk and the real Mk
 - when fctm = 0, the point of decoupling between bilinear and real MK diagram is the point of decompression 
"""

# ---------------------------------------------------------------------------
# Slab
# ---------------------------------------------------------------------------

testing_slab_const = test_slab_construction_c1_3

# ---------------------------------------------------------------------------
# Loads
# ---------------------------------------------------------------------------

print(f"\nLoads:")
print(f"  Live load (Qk):      {test_loads.Qk[0]:.1f} kN/m²")
print(f"  Structural DL:       {testing_slab_const.structural_dead_load():.2f} kN/m²")
print(f"  Non-structural DL:   {testing_slab_const.non_structural_dead_load():.2f} kN/m²")
print(f"  QP-Combination:      {calculate_line_load(testing_slab_const, test_loads, "QUASI-PERMANENT"):.2f} kN/m")

# ---------------------------------------------------------------------------
# M-κ diagram points (support x=0.0 and midspan x=0.5)
# ---------------------------------------------------------------------------
def print_mk_points(label: str, x_norm: float) -> None:
    section = testing_slab_const.slab.section_at(x_norm)
    mk_result = calculate_moment_curvature_sls(
        section,
        n=0,
        include_prestress_branch=True,
        concrete_tension=False
    )
    M_list     = list(-mk_result.m_y / 1e6)       # Nmm → kNm, positive sagging
    kappa_list = list(-mk_result.chi_y * 1000)     # 1/mm → 1/m, positive sagging

    print(f"\n  M     [kNm] = {[round(v, 4) for v in M_list]}")
    print(f"  kappa [1/m] = {[round(v, 6) for v in kappa_list]}")
#
print(f"\n" + "=" * 70)
print("M-κ DIAGRAM POINTS")
print("=" * 70)
#
print(f"\n--- Support (x = 0.0) ---")
print_mk_points("Support", 0.0)
#
print(f"\n--- Midspan (x = 0.5) ---")
print_mk_points("Midspan", 0.5)

mk_results = calculate_moment_curvature_sls(testing_slab_const.slab.section_at(0.5))

#----------------------------------------------------------------------------
# Results from INCA
#----------------------------------------------------------------------------

inca_curvatures = [0.0, 0.0000958, 0.0001916, 0.0002875, 0.0003833, 0.0004791, 0.0005749, 0.0006707, 0.0007665, 0.0008624, 0.0009582, 0.0010540, 0.0012456, 0.0014373, 0.0017247, 0.0022038, 0.0029703, 0.0043118, 0.0068988, 0.0070905, 0.0094859, 0.0117855, 0.0138935, 0.0157140, 0.0172471, 0.0183969, 0.0191635]

inca_moments = [-0.0, 8.6590, 16.9183, 24.6943, 31.8488, 38.0857, 42.7710, 46.4243, 49.5323, 52.2852, 54.7895, 57.1114, 61.3710, 65.2828, 70.7426, 79.2120, 91.9488, 113.2415, 153.0375, 156.1622, 206.8669, 254.0079, 295.3490, 328.9220, 354.8301, 372.0099, 381.7650]
# ---------------------------------------------------------------------------
# Deflection calculation
# ---------------------------------------------------------------------------
print(f"\n" + "=" * 70)
print("DEFLECTION RESULT")
print("=" * 70)

deflection = DeflectionCalculator.calculate_deflection(
    test_slab_construction_c1_3,
    test_loads,
    system="SIMPLE_BEAM",
    combination="QUASI-PERMANENT",
    debug=True,
    extended_debug=True
)

print(f"\n  Deflection:        {deflection:.2f} mm")
print(f"  Deflection/Span:   L/{testing_slab_const.slab.L * 1000 / deflection:.0f} mm ")
print("=" * 70)

# ---------------------------------------------------------------------------
# Plot
# ---------------------------------------------------------------------------

plot_moment_curvature_with_reference(mk_results, inca_curvatures, inca_moments)

plt.show()