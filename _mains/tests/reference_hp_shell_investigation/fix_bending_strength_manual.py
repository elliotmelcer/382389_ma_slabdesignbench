"""
Alternative bending strength calculation for HP shell sections.

PROBLEM: structuralcodes' calculate_bending_strength converges to wrong solution
for test_slab_construction_ref because:
1. It finds M_u = -202 kNm (hogging) instead of +103 kNm (sagging)
2. The curvature is only 33.8% of what it should be
3. The entire section ends up in compression (impossible for N=0 without prestress effects)

SOLUTION: This script implements a manual approach that properly searches
for the maximum POSITIVE (sagging) moment by:
1. Scanning multiple strain profiles
2. Finding the one with maximum positive moment while maintaining N=0
"""

import numpy as np
from copy import deepcopy
from structuralcodes.sections import GenericSection
import matplotlib.pyplot as plt

from core.analysis_core.section_methods import get_strain_at_point


def calculate_bending_strength_sagging(
    section: GenericSection,
    n: float = 0.0,
    eps_cu: float = -0.0035,  # Concrete crushing strain at top
    tolerance: float = 10.0,  # Force tolerance in N
    max_iter: int = 100,
    debug: bool = False,
) -> dict:
    """
    Calculate SAGGING (positive) bending strength by fixing top strain and iterating curvature.

    The key insight: for sagging bending with top in compression:
    - eps_top = eps_cu = -3.5‰ (fixed)
    - chi_y < 0 (negative curvature)
    - eps_bot = eps_top - chi_y * depth > 0 (bottom in tension)

    We iterate chi_y to find N = n equilibrium.
    """

    analysis_section = deepcopy(section)

    # Get section extents
    _, _, zmin, zmax = analysis_section.geometry.calculate_extents()
    section_depth = zmax - zmin

    if debug:
        print(f"[DEBUG] Section: zmin={zmin:.2f}, zmax={zmax:.2f}, depth={section_depth:.2f}")

    # Get calculator
    calculator = analysis_section.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    # For the top fiber at eps_cu:
    # eps(zmax) = eps_0 + chi_y * zmax = eps_cu
    # Therefore: eps_0 = eps_cu - chi_y * zmax

    def get_strain_profile(chi_y):
        eps_0 = eps_cu - chi_y * zmax
        return [eps_0, chi_y, 0.0]

    def get_forces(chi_y):
        strain_profile = get_strain_profile(chi_y)
        N, My, Mz, _ = calculator.integrator.integrate_strain_response_on_geometry(
            analysis_section.geometry,
            strain_profile,
            integration_data=integration_data,
            mesh_size=mesh_size
        )
        return N, My

    # --- SCAN PHASE: Find the curvature range where N crosses zero ---
    # For sagging (positive moment), we need chi_y negative enough that bottom is in tension

    # Physical bound: bottom strain should be positive (tension)
    # eps_bot = eps_cu - chi_y * (zmax - zmin) = eps_cu - chi_y * depth
    # For eps_bot > 0: chi_y < eps_cu / depth
    chi_max_for_tension = eps_cu / section_depth  # This is negative

    if debug:
        print(f"[DEBUG] chi_max_for_tension = {chi_max_for_tension:.2e} (bottom at zero strain)")
        print(f"[DEBUG] For eps_bot = +5‰, need chi_y = {(eps_cu - 0.005)/section_depth:.2e}")

    # Scan a range of curvatures
    chi_values = np.linspace(chi_max_for_tension * 3, chi_max_for_tension * 0.5, 50)
    N_values = []
    M_values = []

    if debug:
        print(f"\n[DEBUG] Scanning curvature range...")

    for chi in chi_values:
        N, My = get_forces(chi)
        N_values.append(N)
        M_values.append(My)

        if debug and len(N_values) % 10 == 0:
            eps_bot = eps_cu - chi * section_depth
            print(f"        chi={chi:.2e}: N={N:+.0f} N, M={My/1e6:+.2f} kNm, eps_bot={eps_bot*1000:+.2f}‰")

    N_values = np.array(N_values)
    M_values = np.array(M_values)

    # Find zero crossings of N - n
    dn = N_values - n
    crossings = []
    for i in range(len(dn) - 1):
        if dn[i] * dn[i+1] < 0:
            crossings.append(i)

    if debug:
        print(f"\n[DEBUG] Found {len(crossings)} zero crossings of N")

    if len(crossings) == 0:
        print("[WARNING] No N=0 crossing found in curvature range!")
        print(f"          N ranges from {N_values.min():.0f} to {N_values.max():.0f}")
        print(f"          Target N = {n}")
        return {
            'section': section,
            'm_u': 0.0,
            'strain_profile': [0.0, 0.0, 0.0],
            'valid': False,
            'reason': 'No equilibrium found'
        }

    # --- REFINEMENT PHASE: Bisection to find exact N=0 ---
    # Take the crossing that gives the highest positive moment
    best_result = None
    best_moment = float('-inf')

    for crossing_idx in crossings:
        chi_a = chi_values[crossing_idx]
        chi_b = chi_values[crossing_idx + 1]
        N_a = N_values[crossing_idx]
        N_b = N_values[crossing_idx + 1]

        dn_a = N_a - n
        dn_b = N_b - n

        # Bisection
        for _ in range(max_iter):
            if abs(dn_a - dn_b) < tolerance:
                break

            chi_c = (chi_a + chi_b) / 2
            N_c, M_c = get_forces(chi_c)
            dn_c = N_c - n

            if dn_c * dn_a < 0:
                chi_b = chi_c
                dn_b = dn_c
            else:
                chi_a = chi_c
                dn_a = dn_c

        # Get final moment
        chi_final = (chi_a + chi_b) / 2
        N_final, M_final = get_forces(chi_final)

        if debug:
            print(f"[DEBUG] Crossing {crossing_idx}: chi={chi_final:.2e}, N={N_final:.0f}, M={M_final/1e6:.2f} kNm")

        if M_final > best_moment:
            best_moment = M_final
            strain_profile = get_strain_profile(chi_final)
            best_result = {
                'section': section,
                'm_u': M_final,
                'strain_profile': strain_profile,
                'chi_y': chi_final,
                'eps_0': strain_profile[0],
                'eps_top': eps_cu,
                'eps_bot': eps_cu - chi_final * section_depth,
                'N_residual': N_final,
                'valid': True,
            }

    if debug and best_result:
        print(f"\n[DEBUG] BEST RESULT:")
        print(f"        M_u = {best_result['m_u']/1e6:.2f} kNm")
        print(f"        chi_y = {best_result['chi_y']:.9f} 1/mm")
        print(f"        eps_top = {best_result['eps_top']*1000:.3f}‰")
        print(f"        eps_bot = {best_result['eps_bot']*1000:.3f}‰")

    return best_result


# ============================================================
# TEST FUNCTION
# ============================================================

def test_manual_calculation():
    """
    Test the manual calculation on hp_ref.
    """
    from structuralcodes import set_design_code
    set_design_code('ec2_2004')

    from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
    from _mains.testing_files.testing_materials import concrete_c50_uls, ref_solidian_Q85_pre_37
    from _mains.testing_files.testing_hp_sections import hp_ref

    from core.analysis_core.section_methods import calculate_bending_strength_uls_Nmm_EC
    from core.visualization_core.visualization import plot_cross_section

    print("=" * 70)
    print("COMPARING STANDARD vs MANUAL BENDING STRENGTH CALCULATION")
    print("=" * 70)

    # Create section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)

    _, _, zmin, zmax = section.geometry.calculate_extents()

    print("\n[1] STANDARD METHOD (structuralcodes):")
    print("-" * 50)
    result_std = calculate_bending_strength_uls_Nmm_EC(section, n=0)

    m_u_std = result_std['m_u']
    strain_std = result_std['strain_profile']
    eps_top_std = get_strain_at_point(strain_std, 0, zmax)
    eps_bot_std = get_strain_at_point(strain_std, 0, zmin)

    print(f"    M_u = {m_u_std/1e6:.2f} kNm")
    print(f"    eps_top = {eps_top_std*1000:.3f}‰")
    print(f"    eps_bot = {eps_bot_std*1000:.3f}‰")
    print(f"    chi_y = {strain_std[1]:.9f} 1/mm")

    print("\n[2] MANUAL METHOD (sagging search):")
    print("-" * 50)
    result_manual = calculate_bending_strength_sagging(section, n=0, debug=True)

    print("\n[3] EXPECTED (INCA2):")
    print("-" * 50)
    print(f"    M_u ≈ 103 kNm")
    print(f"    eps_top = -3.5‰")
    print(f"    eps_bot = +4.978‰")

    print("\n[4] SUMMARY (using absolute values for moment):")
    print("=" * 70)
    print(f"{'Method':<25} {'|M_u| [kNm]':>12} {'eps_top [‰]':>12} {'eps_bot [‰]':>12}")
    print("-" * 70)
    print(f"{'Standard (structuralcodes)':<25} {abs(m_u_std)/1e6:>12.2f} {eps_top_std*1000:>+12.3f} {eps_bot_std*1000:>+12.3f}")
    if result_manual['valid']:
        print(f"{'Manual (sagging)':<25} {abs(result_manual['m_u'])/1e6:>12.2f} {result_manual['eps_top']*1000:>+12.3f} {result_manual['eps_bot']*1000:>+12.3f}")
    print(f"{'INCA2 (expected)':<25} {103.0:>12.2f} {-3.5:>+12.3f} {+4.978:>+12.3f}")
    print("=" * 70)

    # Check if manual result is closer to INCA2
    if result_manual['valid']:
        error_std = abs(abs(m_u_std)/1e6 - 103.0)
        error_manual = abs(abs(result_manual['m_u'])/1e6 - 103.0)
        print(f"\nError vs INCA2:")
        print(f"  Standard: {error_std:.1f} kNm ({error_std/103*100:.1f}%)")
        print(f"  Manual:   {error_manual:.1f} kNm ({error_manual/103*100:.1f}%)")

    # Plot comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot cross-section
    plot_cross_section(section, ax=axes[0])
    axes[0].set_title("HP-Ref Section at Midspan")

    # Plot strain profiles
    ax2 = axes[1]
    z_plot = np.linspace(zmin, zmax, 100)

    # Standard result
    eps_std = strain_std[0] + strain_std[1] * z_plot
    ax2.plot(eps_std * 1000, z_plot, 'r-', linewidth=2, label=f'Standard: M={m_u_std/1e6:.0f} kNm')

    # Manual result
    if result_manual['valid']:
        sp = result_manual['strain_profile']
        eps_manual = sp[0] + sp[1] * z_plot
        ax2.plot(eps_manual * 1000, z_plot, 'b-', linewidth=2, label=f'Manual: M={result_manual["m_u"]/1e6:.0f} kNm')

    # INCA2 expected
    chi_y_inca = (-0.0035 - 0.004978) / (zmax - zmin)
    eps_0_inca = 0.004978 - chi_y_inca * zmin
    eps_inca = eps_0_inca + chi_y_inca * z_plot
    ax2.plot(eps_inca * 1000, z_plot, 'g--', linewidth=2, label='INCA2: M≈103 kNm')

    ax2.axvline(0, color='black', linewidth=0.5)
    ax2.axvline(-3.5, color='gray', linestyle=':', alpha=0.5, label='ε_cu = -3.5‰')
    ax2.set_xlabel('Strain [‰]')
    ax2.set_ylabel('z [mm]')
    ax2.set_title('Strain Profile Comparison')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(r'C:\Users\LJ\Downloads\hp_ref_comparison.png', dpi=150)
    print(f"\n[PLOT SAVED] hp_ref_comparison.png")
    plt.show()

    return result_std, result_manual


if __name__ == "__main__":
    test_manual_calculation()