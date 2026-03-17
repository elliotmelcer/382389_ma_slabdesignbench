"""
Test: Effect of num_points on Method 2 accuracy - FIXED VERSION

Bug fix: Use intercept from polyfit, not M_p directly.
The M-κ curve already has an initial moment offset built in.
"""

import numpy as np
import matplotlib.pyplot as plt

from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic

from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm,
    calculate_prestress_forces_Nmm,
    sls_section,
)
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell

set_design_code('ec2_2004')


def create_section_with_prestress(prestress_factor: float):
    """Create the HP shell section with a given prestress factor."""

    span_L = 7000.0
    width_B = 1520.0
    height = 650.0
    Hx_Hges = 0.2
    thickness = 85.0
    nt = 15
    dy = 190.0
    fck = 30.0
    reinf_area = 100.5

    Hx = Hx_Hges * height
    Hy = (1 - Hx_Hges) * height

    concrete_uls = create_concrete(
        fck=fck,
        constitutive_law='parabolarectangle',
        alpha_cc=0.85,
        gamma_c=1.5,
    )

    epsuk = 10 / 1000
    brittle_elastic = Elastic(220000, eps_u=epsuk)
    initial_strain = prestress_factor * epsuk

    reinforcement = create_reinforcement(
        fyk=2200, Es=220000, ftk=2200, epsuk=epsuk,
        density=1800, constitutive_law=brittle_elastic,
        initial_strain=initial_strain, gamma_s=1.3,
    )

    hp_geom = HPGeometry(B=width_B, L=span_L, Hx=Hx, Hy=Hy, t=thickness, dy=dy, nt=nt)
    hp_shell = HPShell(hp_geom, concrete_uls, reinforcement, reinf_area=reinf_area)

    return hp_shell.section_at(0.5)


def get_mk_curve(section, n: float = 0.0):
    """Get the raw M-κ curve from the library."""
    sls_sec = sls_section(section, concrete_tension=False)
    results = sls_sec.section_calculator.calculate_moment_curvature(
        n=n, num_pre_yield=40, num_post_yield=0
    )
    return results.m_y, results.chi_y


def calculate_kappa_0_method1(section, n: float = 0.0):
    """Method 1: Using M_cr (ground truth when valid)."""
    M_p,_ = calculate_prestress_forces_Nmm(section)  # Nmm

    M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=n)
    if not M_cr_result.get('valid', True):
        return None, None

    M_cr = abs(M_cr_result["m_cr"])  # Nmm
    kappa_cr = abs(M_cr_result["strain_profile"][1])  # 1/mm

    if abs(M_cr - M_p) > 1e-3:
        # Negative sign: prestress creates upward camber (negative curvature)
        kappa_0 = -(M_p * kappa_cr) / (M_cr - M_p)
        return kappa_0, {'M_p': M_p, 'M_cr': M_cr, 'kappa_cr': kappa_cr}
    return 0.0, None


def calculate_kappa_0_method2_fixed(section, num_points: int, n: float = 0.0):
    """
    Method 2 FIXED: Using intercept from linear fit.

    The M-κ curve follows: M = slope * κ + intercept
    At external moment = 0: kappa_0 = -intercept / slope

    But since intercept is negative (prestress effect) and slope is positive,
    we need kappa_0 = intercept / slope to get negative result (upward camber).
    """
    M_array, kappa_array = get_mk_curve(section, n)

    if len(M_array) < num_points:
        return None, None

    # Linear fit: M = slope * κ + intercept
    slope, intercept = np.polyfit(kappa_array[:num_points], M_array[:num_points], 1)

    # At M = 0 (zero external moment):
    # 0 = slope * kappa_0 + intercept
    # kappa_0 = -intercept / slope
    # 
    # However, to match Method 1's sign convention (negative = upward camber),
    # and since intercept is already negative, we use:
    # kappa_0 = intercept / slope (gives negative result)
    if abs(slope) > 1e-6:
        kappa_0 = -intercept / slope
        return kappa_0, {'slope': slope, 'intercept': intercept, 'EI': abs(slope)}
    return 0.0, None


def test_num_points_effect():
    """Test different numbers of points for polyfit."""

    print("=" * 110)
    print("TESTING: Effect of num_points on Method 2 accuracy (FIXED - using intercept)")
    print("=" * 110)
    print()
    print("Ground truth: Method 1 (using M_cr)")
    print("Method 2: kappa_0 = -intercept / slope  (from linear fit of M-κ curve)")
    print()

    prestress_factors = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    num_points_options = [2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40]

    all_results = {n: [] for n in num_points_options}

    # Header
    header = f"{'Prestress':<10}"
    for n in num_points_options:
        header += f"{'n=' + str(n):<9}"
    print(header)
    print("-" * 110)

    for f in prestress_factors:
        section = create_section_with_prestress(f)

        k0_m1, _ = calculate_kappa_0_method1(section)
        if k0_m1 is None:
            continue

        row = f"{f * 100:<10.0f}"

        for n in num_points_options:
            k0_m2, _ = calculate_kappa_0_method2_fixed(section, n)

            if k0_m2 is not None and k0_m1 != 0:
                diff_pct = abs(k0_m1 - k0_m2) / abs(k0_m1) * 100
                all_results[n].append(diff_pct)
                row += f"{diff_pct:<9.1f}"
            else:
                row += f"{'N/A':<9}"

        print(row)

    # Summary
    print()
    print("=" * 110)
    print("SUMMARY: Average difference [%] for each num_points")
    print("=" * 110)

    summary_data = []
    for n in num_points_options:
        if all_results[n]:
            avg = np.mean(all_results[n])
            std = np.std(all_results[n])
            max_diff = np.max(all_results[n])
            min_diff = np.min(all_results[n])
            summary_data.append({
                'num_points': n,
                'avg': avg,
                'std': std,
                'max': max_diff,
                'min': min_diff,
            })
            print(f"  n={n:<3}: avg={avg:>6.2f}%, std={std:>5.2f}%, range=[{min_diff:.1f}%, {max_diff:.1f}%]")

    if summary_data:
        best = min(summary_data, key=lambda x: x['avg'])
        print()
        print(f"  → BEST: n={best['num_points']} with average difference of {best['avg']:.2f}%")

    return all_results, summary_data


def detailed_comparison():
    """Show detailed comparison between methods."""

    print("\n" + "=" * 120)
    print("DETAILED COMPARISON: Method 1 vs Method 2 (Fixed)")
    print("=" * 120)

    prestress_factors = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

    print(
        f"\n{'Prestress':<10} {'kappa_0 M1':<18} {'kappa_0 M2 (n=2)':<18} {'kappa_0 M2 (n=5)':<18} {'Diff n=2 [%]':<14} {'Diff n=5 [%]':<14}")
    print(f"{'[%]':<10} {'[1/m]':<18} {'[1/m]':<18} {'[1/m]':<18} {'':<14} {'':<14}")
    print("-" * 120)

    for f in prestress_factors:
        section = create_section_with_prestress(f)

        k0_m1, info1 = calculate_kappa_0_method1(section)
        k0_m2_n2, info2_n2 = calculate_kappa_0_method2_fixed(section, num_points=2)
        k0_m2_n5, info2_n5 = calculate_kappa_0_method2_fixed(section, num_points=5)

        if k0_m1 is not None and k0_m2_n2 is not None and k0_m2_n5 is not None:
            # Convert to 1/m for display
            k0_m1_display = k0_m1 * 1000
            k0_m2_n2_display = k0_m2_n2 * 1000
            k0_m2_n5_display = k0_m2_n5 * 1000

            diff_n2 = abs(k0_m1 - k0_m2_n2) / abs(k0_m1) * 100
            diff_n5 = abs(k0_m1 - k0_m2_n5) / abs(k0_m1) * 100

            print(
                f"{f * 100:<10.0f} {k0_m1_display:<18.6f} {k0_m2_n2_display:<18.6f} {k0_m2_n5_display:<18.6f} {diff_n2:<14.1f} {diff_n5:<14.1f}")

    # Also show sign comparison
    print("\n" + "-" * 120)
    print("SIGN CHECK: All kappa_0 values should be NEGATIVE (upward camber from prestress)")
    print("-" * 120)

    for f in [0.30, 0.50]:
        section = create_section_with_prestress(f)
        k0_m1, _ = calculate_kappa_0_method1(section)
        k0_m2, _ = calculate_kappa_0_method2_fixed(section, num_points=2)

        print(f"  Prestress {f * 100:.0f}%:")
        print(f"    Method 1: kappa_0 = {k0_m1 * 1000:.6f} 1/m  ({'NEGATIVE ✓' if k0_m1 < 0 else 'POSITIVE ✗'})")
        print(f"    Method 2: kappa_0 = {k0_m2 * 1000:.6f} 1/m  ({'NEGATIVE ✓' if k0_m2 < 0 else 'POSITIVE ✗'})")


def investigate_intercept_vs_mp():
    """Compare the intercept from polyfit with M_p."""

    print("\n" + "=" * 110)
    print("INVESTIGATING: Intercept vs M_p")
    print("=" * 110)
    print("\nThe intercept from the M-κ fit should be related to M_p (prestress moment).")
    print()

    prestress_factors = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

    print(f"{'Prestress':<10} {'M_p [kNm]':<15} {'Intercept [kNm]':<18} {'Ratio (Int/M_p)':<15}")
    print("-" * 60)

    for f in prestress_factors:
        section = create_section_with_prestress(f)

        M_p_Nmm,_ = calculate_prestress_forces_Nmm(section)  # kNm
        M_p_kNm = M_p_Nmm / 1e6

        M_array, kappa_array = get_mk_curve(section)
        slope, intercept = np.polyfit(kappa_array[:5], M_array[:5], 1)
        intercept_kNm = intercept / 1e6  # kNm

        ratio = intercept_kNm / M_p_kNm if abs(M_p_kNm) > 1e-6 else 0

        print(f"{f * 100:<10.0f} {M_p_kNm:<15.2f} {intercept_kNm:<18.2f} {ratio:<15.3f}")

    print()
    print("[NOTE] The ratio shows how the M-κ intercept relates to the prestress moment.")
    print("       A consistent ratio suggests a predictable relationship.")


def plot_mk_with_extrapolation():
    """Plot M-κ curve with extrapolation to M=0."""

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    section = create_section_with_prestress(0.35)
    M_array, kappa_array = get_mk_curve(section)

    # Get both kappa_0 values
    k0_m1, info1 = calculate_kappa_0_method1(section)
    k0_m2, info2 = calculate_kappa_0_method2_fixed(section, num_points=5)

    # Convert to display units
    M_kNm = np.array(M_array) / 1e6
    kappa_1m = np.array(kappa_array) * 1000  # 1/m

    # Plot 1: Full curve with extrapolation
    ax1 = axes[0]
    ax1.plot(kappa_1m, M_kNm, 'b-', linewidth=2, label='M-κ curve')

    # Linear fit
    slope, intercept = np.polyfit(kappa_array[:5], M_array[:5], 1)
    kappa_extrap = np.linspace(k0_m2 * 0.9, kappa_array[10], 50)
    M_extrap = (slope * kappa_extrap + intercept) / 1e6
    ax1.plot(kappa_extrap * 1000, M_extrap, 'r--', linewidth=2, label='Linear fit (n=5)')

    # Mark kappa_0 points
    if k0_m1 is not None:
        ax1.axvline(x=k0_m1 * 1000, color='green', linestyle=':', linewidth=2,
                    label=f'κ₀ Method 1: {k0_m1 * 1000:.5f} 1/m')
        ax1.plot(k0_m1 * 1000, 0, 'go', markersize=10)

    if k0_m2 is not None:
        ax1.axvline(x=k0_m2 * 1000, color='orange', linestyle=':', linewidth=2,
                    label=f'κ₀ Method 2: {k0_m2 * 1000:.5f} 1/m')
        ax1.plot(k0_m2 * 1000, 0, 'o', color='orange', markersize=10)

    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.set_xlabel('Curvature κ [1/m]')
    ax1.set_ylabel('Moment M [kNm]')
    ax1.set_title('M-κ Curve with Extrapolation (35% prestress)')
    ax1.legend(loc='lower right')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Zoomed to initial region
    ax2 = axes[1]
    n_show = 15
    ax2.plot(kappa_1m[:n_show], M_kNm[:n_show], 'bo-', linewidth=2, markersize=6, label='M-κ data')
    ax2.plot(kappa_extrap * 1000, M_extrap, 'r--', linewidth=2, label='Linear extrapolation')

    if k0_m1 is not None:
        ax2.plot(k0_m1 * 1000, 0, 'go', markersize=12, label=f'κ₀ M1: {k0_m1 * 1000:.5f}')
    if k0_m2 is not None:
        ax2.plot(k0_m2 * 1000, 0, 'o', color='orange', markersize=12, label=f'κ₀ M2: {k0_m2 * 1000:.5f}')

    ax2.axhline(y=0, color='k', linewidth=0.5)
    ax2.set_xlabel('Curvature κ [1/m]')
    ax2.set_ylabel('Moment M [kNm]')
    ax2.set_title('Zoomed: Initial Region with κ₀')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('mk_extrapolation_comparison.png', dpi=150)
    print("\nSaved plot to: mk_extrapolation_comparison.png")
    plt.show()


if __name__ == "__main__":
    # Test effect of num_points
    all_results, summary_data = test_num_points_effect()

    # Detailed comparison
    detailed_comparison()

    # Investigate relationship between intercept and M_p
    investigate_intercept_vs_mp()

    # Plot comparison
    plot_mk_with_extrapolation()

    print("\n" + "=" * 110)
    print("RECOMMENDATION")
    print("=" * 110)
    if summary_data:
        best = min(summary_data, key=lambda x: x['avg'])
        best_consistent = min(summary_data, key=lambda x: x['avg'] + x['std'])

        print(f"\n  Best accuracy:    n={best['num_points']} (avg diff: {best['avg']:.2f}%)")
        print(
            f"  Best consistency: n={best_consistent['num_points']} (avg+std: {best_consistent['avg'] + best_consistent['std']:.2f}%)")