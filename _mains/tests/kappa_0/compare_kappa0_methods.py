"""
Test: Compare methods for calculating initial curvature from prestressing (kappa_0)
FIXED VERSION - Correct sign handling for Method 2

Method 1 (Current): Using M_cr
    kappa_0 = (M_p * kappa_cr) / (M_cr - M_p)

Method 2 (Alternative): Using initial slope of M-κ curve
    EI = dM/dκ (flexural stiffness from initial slope)
    kappa_0 = -M_p / EI (extrapolate back from M=0)

Method 3 (Alternative): Using M_cr and kappa=0
    kappa_0 = - M_int * kappa_cr / (M_cr - M_int)
"""

import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy

from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic

from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm,
    calculate_prestress_forces_Nmm,
    sls_section,
)
from slab_construction.slabs.hp_slab.hp_model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell

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

    return hp_shell.section_at(0.5), initial_strain


def get_mk_curve_from_library(section, n: float = 0.0):
    """Get the raw M-κ curve from the library (without prestress branch)."""

    sls_sec = sls_section(section, constitutive_law="NONE_PARABOLIC")

    results = sls_sec.section_calculator.calculate_moment_curvature(
        n=n,
        num_pre_yield=40,
        num_post_yield=0
    )

    # Return raw values (typically negative for sagging)
    return results.m_y, results.chi_y


def calculate_kappa_0_method1(section, n: float = 0.0):
    """
    Method 1: Calculate kappa_0 using M_cr and kappa_cr

    Formula: kappa_0 = (M_p * kappa_cr) / (M_cr - M_p)
    """
    M_p_Nmm, _ = calculate_prestress_forces_Nmm(section)
    M_p_kNm = M_p_Nmm / 1e6

    M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=n)

    if not M_cr_result.get('valid', True):
        return {
            'valid': False,
            'reason': M_cr_result.get('reason', 'M_cr calculation failed'),
            'M_p_kNm': M_p_kNm,
            'kappa_0': None,
        }

    M_cr = abs(M_cr_result["m_cr"])  # Nmm
    kappa_cr = abs(M_cr_result["strain_profile"][1])  # 1/mm

    if abs(M_cr - M_p_Nmm) > 1e-3:
        kappa_0 = (M_p_Nmm * kappa_cr) / (M_cr - M_p_Nmm)  # 1/mm
    else:
        kappa_0 = 0.0

    return {
        'valid': True,
        'kappa_0': kappa_0,
        'M_p_kNm': M_p_kNm,
        'M_cr_kNm': M_cr / 1e6,
        'kappa_cr': kappa_cr,
    }


def calculate_kappa_0_method2(section, n: float = 0.0, num_points: int = 2):
    """
    Method 2: Calculate kappa_0 using initial slope of M-κ curve

    The M-κ curve has initial slope EI = dM/dκ
    The prestress moment M_p creates initial curvature:
        kappa_0 = -M_p / EI

    Since prestress creates upward camber (negative curvature for sagging convention),
    and M_p is positive, we need: kappa_0 = -M_p / EI (negative result)
    """
    M_p_Nmm, _ = calculate_prestress_forces_Nmm(section)
    M_p_kNm = M_p_Nmm / 1e6

    M_array, kappa_array = get_mk_curve_from_library(section, n)

    if len(M_array) < num_points:
        return {
            'valid': False,
            'reason': 'Not enough points in M-κ curve',
            'M_p_kNm': M_p_kNm,
            'kappa_0': None,
        }

    M_initial = M_array[:num_points]
    kappa_initial = kappa_array[:num_points]

    slope, intercept = np.polyfit(kappa_initial, M_initial, 1)

    EI = abs(slope)

    if EI > 1e-6:
        kappa_0 = -M_p_Nmm / EI
    else:
        kappa_0 = 0.0

    return {
        'valid': True,
        'kappa_0': kappa_0,
        'M_p_kNm': M_p_kNm,
        'EI': EI,
        'slope_raw': slope,
        'intercept': intercept,
    }


def calculate_kappa_0_method3(section, n: float = 0.0, num_points: int = 5):
    """
    Method 3: Calculate kappa_0 using M_cr and kappa=0

    Formula: kappa_0 = - M_int * kappa_cr / (M_cr - M_int)
    """

    sec_sls = sls_section(section, constitutive_law="TENSTIFF_PARABOLIC")

    # Cracking Point
    M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=n)
    M_cr_Nmm = abs(M_cr_result["m_cr"])
    kappa_cr = abs(M_cr_result["strain_profile"][1])

    # Intersect Point
    Mk_res_0 = sec_sls.section_calculator.calculate_moment_curvature(chi=[0.0])
    M_int_Nmm = abs(Mk_res_0.m_y[0])

    # Kappa_0
    kappa_0 = - M_int_Nmm * kappa_cr / (M_cr_Nmm - M_int_Nmm)

    return kappa_0


def compare_methods(prestress_factors: list):
    """Compare all three methods across a range of prestress factors."""

    print("=" * 115)
    print("COMPARISON: kappa_0 CALCULATION METHODS")
    print("=" * 115)
    print()
    print("Method 1: kappa_0 = (M_p * kappa_cr) / (M_cr - M_p)")
    print("Method 2: kappa_0 = -M_p / EI  (EI from initial slope of M-κ curve)")
    print("Method 3: kappa_0 = -M_int * kappa_cr / (M_cr - M_int)")
    print()
    print("-" * 115)
    print(f"{'Prestress':<10} {'M_p':<12} {'M_cr':<12} {'kappa_0 (M1)':<16} {'kappa_0 (M2)':<16} {'kappa_0 (M3)':<16} {'Diff M1-M2':<12} {'Diff M1-M3':<12} {'Status'}")
    print(f"{'[%]':<10} {'[kNm]':<12} {'[kNm]':<12} {'[1/m]':<16} {'[1/m]':<16} {'[1/m]':<16} {'[%]':<12} {'[%]':<12} {''}")
    print("-" * 115)

    results = []

    for f in prestress_factors:
        section, _ = create_section_with_prestress(f)

        r1 = calculate_kappa_0_method1(section)
        r2 = calculate_kappa_0_method2(section)

        M_p = r1['M_p_kNm']
        M_cr = r1.get('M_cr_kNm', float('nan'))

        if r1['valid'] and r2['valid']:
            k0_m1 = r1['kappa_0'] * 1000
            k0_m2 = r2['kappa_0'] * 1000
            k0_m3 = calculate_kappa_0_method3(section) * 1000

            diff_pct_m2 = abs(k0_m1 - k0_m2) / abs(k0_m1) * 100 if abs(k0_m1) > 1e-9 else 0.0
            diff_pct_m3 = abs(k0_m1 - k0_m3) / abs(k0_m1) * 100 if abs(k0_m1) > 1e-9 else 0.0

            status = "OK" if diff_pct_m2 < 20 and diff_pct_m3 < 20 else "DIFF"

            print(f"{f*100:<10.1f} {M_p:<12.2f} {M_cr:<12.2f} {k0_m1:<16.6f} {k0_m2:<16.6f} {k0_m3:<16.6f} {diff_pct_m2:<12.1f} {diff_pct_m3:<12.1f} {status}")

            results.append({
                'factor': f,
                'M_p': M_p,
                'M_cr': M_cr,
                'kappa_0_m1': k0_m1,
                'kappa_0_m2': k0_m2,
                'kappa_0_m3': k0_m3,
                'diff_pct_m2': diff_pct_m2,
                'diff_pct_m3': diff_pct_m3,
                'both_valid': True,
                'm1_valid': True,
                'm2_valid': True,
            })
        else:
            k0_m2 = r2['kappa_0'] * 1000 if r2['valid'] else None
            k0_m1 = r1['kappa_0'] * 1000 if r1['valid'] else None
            k0_m3 = calculate_kappa_0_method3(section) * 1000 if r1['valid'] else None

            m1_str = f"{k0_m1:.6f}" if k0_m1 is not None else "INVALID"
            m2_str = f"{k0_m2:.6f}" if k0_m2 is not None else "INVALID"
            m3_str = f"{k0_m3:.6f}" if k0_m3 is not None else "INVALID"

            status = "M2/M3 fallback" if r2['valid'] and not r1['valid'] else "PROBLEM"

            print(f"{f*100:<10.1f} {M_p:<12.2f} {'inf' if not r1['valid'] else M_cr:<12} {m1_str:<16} {m2_str:<16} {m3_str:<16} {'N/A':<12} {'N/A':<12} {status}")

            results.append({
                'factor': f,
                'M_p': M_p,
                'M_cr': M_cr if r1['valid'] else float('inf'),
                'kappa_0_m1': k0_m1,
                'kappa_0_m2': k0_m2,
                'kappa_0_m3': k0_m3,
                'diff_pct_m2': None,
                'diff_pct_m3': None,
                'both_valid': False,
                'm1_valid': r1['valid'],
                'm2_valid': r2['valid'],
            })

    return results


def test_fallback_scenario():
    """
    Test the scenario where M_cr is invalid but we need kappa_0.
    This simulates what happens in calculate_moment_curvature_sls.
    """

    print("\n" + "=" * 115)
    print("FALLBACK SCENARIO TEST")
    print("=" * 115)
    print("\nSimulating calculate_moment_curvature_sls behavior:")
    print("  - If M_cr is valid: use Method 1")
    print("  - If M_cr is invalid: use Method 2 or Method 3 as fallback")
    print()

    factors = [0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70]

    print(f"{'Prestress':<10} {'M_cr Valid':<12} {'Method Used':<20} {'kappa_0 [1/m]':<18} {'Notes'}")
    print("-" * 85)

    for f in factors:
        section, _ = create_section_with_prestress(f)

        r1 = calculate_kappa_0_method1(section)
        r2 = calculate_kappa_0_method2(section)

        if r1['valid']:
            method = "Method 1"
            kappa_0 = r1['kappa_0'] * 1000
            notes = f"M_cr = {r1['M_cr_kNm']:.1f} kNm"
        elif r2['valid']:
            method = "Method 2 (fallback)"
            kappa_0 = r2['kappa_0'] * 1000
            notes = f"EI = {r2['EI']:.2e} Nmm²"
        else:
            method = "Method 3 (fallback)"
            kappa_0 = calculate_kappa_0_method3(section) * 1000
            notes = "Methods 1 & 2 failed"

        m1_valid_str = "Yes" if r1['valid'] else "No"

        print(f"{f*100:<10.1f} {m1_valid_str:<12} {method:<20} {kappa_0:<18.6f} {notes}")


def plot_comparison(results: list):
    """Plot the comparison between all three methods."""

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    valid_results = [r for r in results if r['both_valid']]

    factors     = [r['factor'] * 100 for r in valid_results]
    k0_m1       = [r['kappa_0_m1']  for r in valid_results]
    k0_m2       = [r['kappa_0_m2']  for r in valid_results]
    k0_m3       = [r['kappa_0_m3']  for r in valid_results]
    diff_pct_m2 = [r['diff_pct_m2'] for r in valid_results]
    diff_pct_m3 = [r['diff_pct_m3'] for r in valid_results]

    # Plot 1: All three methods
    ax1 = axes[0]
    ax1.plot(factors, k0_m1, 'bo-',  linewidth=2, markersize=8, label='Method 1 (M_cr)')
    ax1.plot(factors, k0_m2, 'rs--', linewidth=2, markersize=8, label='Method 2 (slope)')
    ax1.plot(factors, k0_m3, 'g^-.', linewidth=2, markersize=8, label='Method 3 (M_int)')
    ax1.set_xlabel('Prestress [%]')
    ax1.set_ylabel('κ₀ [1/m]')
    ax1.set_title('Initial Curvature: All Methods')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linewidth=0.5)

    # Plot 2: Differences (grouped bars)
    ax2 = axes[1]
    x = np.array(factors)
    w = 1.5
    ax2.bar(x - w / 2, diff_pct_m2, width=w, color='steelblue', alpha=0.7, label='M1 vs M2')
    ax2.bar(x + w / 2, diff_pct_m3, width=w, color='orange',    alpha=0.7, label='M1 vs M3')
    ax2.axhline(y=20, color='red', linestyle='--', linewidth=2, label='20% threshold')
    ax2.set_xlabel('Prestress [%]')
    ax2.set_ylabel('Difference [%]')
    ax2.set_title('Difference Between Methods')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: Correlation (M2 and M3 vs M1)
    ax3 = axes[2]
    sc2 = ax3.scatter(k0_m1, k0_m2, s=100, marker='s', c=factors, cmap='viridis',  edgecolors='black', label='M2 vs M1')
    sc3 = ax3.scatter(k0_m1, k0_m3, s=100, marker='^', c=factors, cmap='plasma',   edgecolors='black', label='M3 vs M1', alpha=0.7)

    min_val = min(min(k0_m1), min(k0_m2), min(k0_m3))
    max_val = max(max(k0_m1), max(k0_m2), max(k0_m3))
    ax3.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect match')

    ax3.set_xlabel('κ₀ Method 1 [1/m]')
    ax3.set_ylabel('κ₀ Methods 2 & 3 [1/m]')
    ax3.set_title('Correlation vs Method 1')
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(min(factors), max(factors)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax3)
    cbar.set_label('Prestress [%]')

    plt.tight_layout()
    plt.savefig('kappa_0_comparison_fixed.png', dpi=150)
    print("\nSaved plot to: kappa_0_comparison_fixed.png")
    plt.show()


if __name__ == "__main__":
    prestress_factors = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

    results = compare_methods(prestress_factors)

    test_fallback_scenario()

    plot_comparison(results)

    print("\n" + "=" * 115)
    print("SUMMARY")
    print("=" * 115)
    valid_results = [r for r in results if r['both_valid']]
    if valid_results:
        avg_diff_m2 = np.mean([r['diff_pct_m2'] for r in valid_results])
        max_diff_m2 = np.max([r['diff_pct_m2'] for r in valid_results])
        avg_diff_m3 = np.mean([r['diff_pct_m3'] for r in valid_results])
        max_diff_m3 = np.max([r['diff_pct_m3'] for r in valid_results])

        print(f"  M1 vs M2 - Average: {avg_diff_m2:.1f}%   Maximum: {max_diff_m2:.1f}%")
        print(f"  M1 vs M3 - Average: {avg_diff_m3:.1f}%   Maximum: {max_diff_m3:.1f}%")
        print()

        if avg_diff_m2 < 20 and avg_diff_m3 < 20:
            print("  ✓ Methods 2 and 3 are both viable fallbacks when Method 1 (M_cr) fails!")
        elif avg_diff_m2 < 20:
            print("  ✓ Method 2 is a viable fallback. Method 3 differs significantly.")
        elif avg_diff_m3 < 20:
            print("  ✓ Method 3 is a viable fallback. Method 2 differs significantly.")
        else:
            print("  ⚠ All methods differ significantly - investigate further")