"""
Investigation: Why does initial_strain > 0.393 * epsuk cause nonsensical results?

This script investigates the threshold behavior around 39.2% - 39.3% prestress.
"""

import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt

from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic

from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm,
    calculate_moment_curvature_sls,
    sls_section,
)
from core.visualization_core.visualization import plot_cross_section
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell

set_design_code('ec2_2004')


def create_section_with_prestress(prestress_factor: float):
    """Create the HP shell section with a given prestress factor."""

    # Fixed geometry parameters
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

    # Concrete
    concrete_uls = create_concrete(
        fck=fck,
        constitutive_law='parabolarectangle',
        alpha_cc=0.85,
        gamma_c=1.5,
        name=f"C{fck} ULS"
    )

    # Reinforcement with variable prestress
    fyk = 2200
    ftk = 2200
    Es = 220000
    epsuk = 10 / 1000  # 10 promille
    density = 1800

    brittle_elastic = Elastic(Es, eps_u=epsuk)
    initial_strain = prestress_factor * epsuk

    reinforcement = create_reinforcement(
        fyk=fyk,
        Es=Es,
        ftk=ftk,
        epsuk=epsuk,
        density=density,
        constitutive_law=brittle_elastic,
        initial_strain=initial_strain,
        gamma_s=1.3,
        name=f"Q142 prestressed {prestress_factor * 100:.1f}%"
    )

    # Create HP geometry and shell
    hp_geom = HPGeometry(
        B=width_B, L=span_L, Hx=Hx, Hy=Hy, t=thickness, dy=dy, nt=nt
    )
    hp_shell = HPShell(hp_geom, concrete_uls, reinforcement, reinf_area=reinf_area)

    return hp_shell.section_at(0.5), initial_strain, Es, epsuk


def analyze_prestress_effect(prestress_factor: float, verbose: bool = True):
    """Analyze the effect of a given prestress level on the cracking moment."""

    section, initial_strain, Es, epsuk = create_section_with_prestress(prestress_factor)

    # Get section properties
    _, _, zmin, zmax = section.geometry.calculate_extents()
    cz = section.gross_properties.cz

    # Get reinforcement info
    reinf_positions = [pg.point.y for pg in section.geometry.point_geometries]
    reinf_areas = [pg.area for pg in section.geometry.point_geometries]
    total_reinf_area = sum(reinf_areas)
    avg_reinf_z = sum(z * a for z, a in zip(reinf_positions, reinf_areas)) / total_reinf_area

    # Calculate prestress force
    prestress_force = total_reinf_area * initial_strain * Es  # N
    prestress_force_kN = prestress_force / 1000

    # Get concrete properties
    sls_sec = sls_section(section, concrete_tension=True)
    conc = None
    for geo in sls_sec.geometry.geometries:
        if hasattr(geo, 'concrete') and geo.concrete:
            conc = geo.material
            break

    Ecm = conc.Ecm
    fctm = conc.fctm
    eps_ctm = fctm / Ecm  # Cracking strain

    # Calculate cracking moment
    try:
        m_cr_result = calculate_cracking_moment_sls_Nmm(section, n=0)
        m_cr = m_cr_result["m_cr"] / 1e6  # kNm
        strain_profile = m_cr_result["strain_profile"]
        eps_0, chi_y, _ = strain_profile

        # Calculate strains at key points
        eps_bottom = eps_0 + chi_y * zmin
        eps_top = eps_0 + chi_y * zmax
        eps_reinf_avg = eps_0 + chi_y * avg_reinf_z

        # Total strain in reinforcement (bending + initial)
        eps_reinf_total = eps_reinf_avg + initial_strain

        success = True

    except Exception as e:
        m_cr = np.nan
        eps_0 = np.nan
        chi_y = np.nan
        eps_bottom = np.nan
        eps_top = np.nan
        eps_reinf_avg = np.nan
        eps_reinf_total = np.nan
        success = False
        if verbose:
            print(f"  ERROR: {e}")

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"Prestress factor: {prestress_factor:.4f} ({prestress_factor * 100:.2f}%)")
        print(f"{'=' * 60}")
        print(f"  initial_strain = {initial_strain:.6f}")
        print(f"  Prestress force = {prestress_force_kN:.1f} kN")
        print(f"  eps_ctm (cracking strain) = {eps_ctm:.6f}")
        print(f"")
        print(f"  Section geometry:")
        print(f"    zmin = {zmin:.2f} mm, zmax = {zmax:.2f} mm")
        print(f"    cz = {cz:.2f} mm")
        print(f"    avg reinforcement z = {avg_reinf_z:.2f} mm")
        print(f"")

        if success:
            print(f"  Cracking moment result:")
            print(f"    m_cr = {m_cr:.4f} kNm")
            print(f"    eps_0 = {eps_0:.6f}")
            print(f"    chi_y = {chi_y:.9f} 1/mm")
            print(f"")
            print(f"  Strain at cracking:")
            print(f"    eps(bottom) = {eps_bottom:.6f} (should be ~{eps_ctm:.6f})")
            print(f"    eps(top) = {eps_top:.6f}")
            print(f"    eps(reinf, bending only) = {eps_reinf_avg:.6f}")
            print(f"    eps(reinf, total) = {eps_reinf_total:.6f}")
            print(f"")

            # Physical sanity checks
            print(f"  Sanity checks:")
            bottom_ok = abs(eps_bottom - eps_ctm) < 1e-5
            print(f"    Bottom at cracking strain? {bottom_ok}")

            # Is the reinforcement yielding or beyond ultimate?
            if eps_reinf_total > epsuk:
                print(f"    ⚠️  REINF STRAIN > ULTIMATE! ({eps_reinf_total:.6f} > {epsuk:.6f})")
            elif eps_reinf_total < 0:
                print(f"    ⚠️  REINF IN COMPRESSION at cracking! (eps = {eps_reinf_total:.6f})")
            else:
                print(f"    Reinf strain OK (0 < {eps_reinf_total:.6f} < {epsuk:.6f})")

            # Check curvature sign
            if chi_y > 0:
                print(f"    ⚠️  chi_y is POSITIVE - unusual for sagging moment!")
            else:
                print(f"    chi_y is negative (normal for sagging)")

    return {
        'prestress_factor': prestress_factor,
        'initial_strain': initial_strain,
        'prestress_force_kN': prestress_force_kN,
        'm_cr_kNm': m_cr,
        'eps_0': eps_0,
        'chi_y': chi_y,
        'eps_bottom': eps_bottom,
        'eps_top': eps_top,
        'eps_reinf_bending': eps_reinf_avg,
        'eps_reinf_total': eps_reinf_total,
        'eps_ctm': eps_ctm,
        'epsuk': epsuk,
        'success': success,
    }


def scan_prestress_range():
    """Scan a range of prestress factors to find the threshold."""

    print("=" * 70)
    print("SCANNING PRESTRESS RANGE TO FIND THRESHOLD")
    print("=" * 70)

    # Coarse scan first
    factors_coarse = np.linspace(0.30, 0.50, 21)

    results = []
    for f in factors_coarse:
        r = analyze_prestress_effect(f, verbose=False)
        results.append(r)
        status = "OK" if r['success'] and abs(r['m_cr_kNm']) < 1000 else "PROBLEM"
        print(f"  {f:.3f} ({f * 100:.1f}%): m_cr = {r['m_cr_kNm']:>10.2f} kNm, "
              f"chi_y = {r['chi_y']:.2e}, eps_reinf_total = {r['eps_reinf_total']:.6f} [{status}]")

    # Fine scan around threshold
    print("\n" + "=" * 70)
    print("FINE SCAN AROUND THRESHOLD (0.390 - 0.395)")
    print("=" * 70)

    factors_fine = np.linspace(0.390, 0.395, 51)

    results_fine = []
    for f in factors_fine:
        r = analyze_prestress_effect(f, verbose=False)
        results_fine.append(r)
        status = "OK" if r['success'] and abs(r['m_cr_kNm']) < 1000 else "PROBLEM"
        print(f"  {f:.4f} ({f * 100:.2f}%): m_cr = {r['m_cr_kNm']:>10.2f} kNm, "
              f"chi_y = {r['chi_y']:.2e}, eps_reinf_total = {r['eps_reinf_total']:.6f} [{status}]")

    return results, results_fine


def investigate_threshold():
    """Deep investigation at the threshold."""

    print("\n" + "=" * 70)
    print("DETAILED INVESTIGATION AT THRESHOLD")
    print("=" * 70)

    # Just below threshold
    print("\n--- BELOW THRESHOLD (0.392) ---")
    r_below = analyze_prestress_effect(0.392, verbose=True)

    # Just above threshold
    print("\n--- ABOVE THRESHOLD (0.393) ---")
    r_above = analyze_prestress_effect(0.393, verbose=True)

    # Analysis
    print("\n" + "=" * 70)
    print("THRESHOLD ANALYSIS")
    print("=" * 70)

    print(f"\nAt 0.392:")
    print(f"  m_cr = {r_below['m_cr_kNm']:.4f} kNm")
    print(f"  eps_reinf_total = {r_below['eps_reinf_total']:.6f}")

    print(f"\nAt 0.393:")
    print(f"  m_cr = {r_above['m_cr_kNm']:.4f} kNm")
    print(f"  eps_reinf_total = {r_above['eps_reinf_total']:.6f}")

    # Check if reinforcement is hitting a limit
    epsuk = r_below['epsuk']

    print(f"\n[KEY INSIGHT]")
    print(f"  Ultimate strain epsuk = {epsuk:.6f}")
    print(f"  At 0.392: eps_reinf_total = {r_below['eps_reinf_total']:.6f} "
          f"({r_below['eps_reinf_total'] / epsuk * 100:.1f}% of epsuk)")
    print(f"  At 0.393: eps_reinf_total = {r_above['eps_reinf_total']:.6f} "
          f"({r_above['eps_reinf_total'] / epsuk * 100:.1f}% of epsuk)")

    # What initial strain brings reinforcement to exactly epsuk at cracking?
    # eps_reinf_total = initial_strain + eps_reinf_bending
    # At limit: epsuk = initial_strain + eps_reinf_bending
    # So: initial_strain_limit = epsuk - eps_reinf_bending

    eps_reinf_bending_typical = r_below['eps_reinf_bending']
    initial_strain_limit = epsuk - eps_reinf_bending_typical
    prestress_limit = initial_strain_limit / epsuk

    print(f"\n[CALCULATED LIMIT]")
    print(f"  Typical bending strain at reinf = {eps_reinf_bending_typical:.6f}")
    print(f"  Max initial_strain before reinf exceeds epsuk = {initial_strain_limit:.6f}")
    print(f"  This corresponds to prestress factor = {prestress_limit:.4f} ({prestress_limit * 100:.2f}%)")

    return r_below, r_above


def plot_comparison(factor_ok: float = 0.392, factor_bad: float = 0.40):
    """Plot moment-curvature diagrams for comparison."""

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    for idx, factor in enumerate([factor_ok, factor_bad]):
        section, initial_strain, Es, epsuk = create_section_with_prestress(factor)

        # Get m_cr result
        try:
            m_cr_result = calculate_cracking_moment_sls_Nmm(section, n=0)
            m_cr = m_cr_result["m_cr"] / 1e6
            strain_profile = m_cr_result["strain_profile"]
        except Exception as e:
            print(f"Error for factor {factor}: {e}")
            continue

        # Get section geometry
        _, _, zmin, zmax = section.geometry.calculate_extents()
        cz = section.gross_properties.cz

        # Plot 1: Cross-section
        ax1 = axes[idx, 0]
        plot_cross_section(section, ax=ax1, x=0.5)
        ax1.set_title(f"Section (prestress={factor * 100:.1f}%)")

        # Plot 2: Strain profile at cracking
        ax2 = axes[idx, 1]
        eps_0, chi_y, _ = strain_profile
        z_range = np.linspace(zmin, zmax, 100)
        eps_range = eps_0 + chi_y * z_range

        ax2.plot(eps_range * 1000, z_range, 'b-', linewidth=2, label='Strain profile')
        ax2.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        ax2.axhline(y=cz, color='r', linestyle='--', label=f'Centroid (z={cz:.0f}mm)')

        # Mark cracking strain
        conc = None
        sls_sec = sls_section(section, concrete_tension=True)
        for geo in sls_sec.geometry.geometries:
            if hasattr(geo, 'concrete') and geo.concrete:
                conc = geo.material
                break
        eps_ctm = conc.fctm / conc.Ecm
        ax2.axvline(x=eps_ctm * 1000, color='g', linestyle=':', label=f'eps_ctm')

        # Mark reinforcement positions
        for pg in section.geometry.point_geometries:
            z_s = pg.point.y
            eps_s = eps_0 + chi_y * z_s
            ax2.plot(eps_s * 1000, z_s, 'ko', markersize=3, alpha=0.5)

        ax2.set_xlabel('Strain ε [‰]')
        ax2.set_ylabel('z [mm]')
        ax2.set_title(f'Strain at cracking\nm_cr = {m_cr:.2f} kNm')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)

        # Plot 3: Moment-curvature
        ax3 = axes[idx, 2]
        try:
            mk_result = calculate_moment_curvature_sls(
                section, n=0, include_prestress_branch=True, concrete_tension=False
            )
            M_array = -mk_result.m_y / 1e6  # kNm
            kappa_array = -mk_result.chi_y * 1000  # 1/m

            ax3.plot(kappa_array, M_array, 'b-', linewidth=2)
            ax3.axhline(y=abs(m_cr), color='r', linestyle='--', label=f'|m_cr| = {abs(m_cr):.1f} kNm')
            ax3.set_xlabel('Curvature κ [1/m]')
            ax3.set_ylabel('Moment M [kNm]')
            ax3.set_title(f'M-κ diagram (prestress={factor * 100:.1f}%)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)

            # Set reasonable limits
            ax3.set_xlim(left=min(0, min(kappa_array) * 1.1))
            ax3.set_ylim(bottom=0)

        except Exception as e:
            ax3.text(0.5, 0.5, f'Error: {e}', transform=ax3.transAxes,
                     ha='center', va='center')

    axes[0, 0].set_ylabel(f'OK (prestress={factor_ok * 100:.1f}%)', fontsize=12, fontweight='bold')
    axes[1, 0].set_ylabel(f'PROBLEM (prestress={factor_bad * 100:.1f}%)', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('prestress_threshold_comparison.png', dpi=150)
    print("\nSaved comparison plot to: prestress_threshold_comparison.png")
    plt.show()


def investigate_constitutive_law():
    """Check how the Elastic constitutive law behaves near eps_u."""

    print("\n" + "=" * 70)
    print("REINFORCEMENT CONSTITUTIVE LAW INVESTIGATION")
    print("=" * 70)

    Es = 220000
    epsuk = 0.01  # 10 promille

    brittle_elastic = Elastic(Es, eps_u=epsuk)

    print(f"\nElastic law parameters:")
    print(f"  Es = {Es} MPa")
    print(f"  eps_u = {epsuk}")

    # Test strains around the limit
    test_strains = [0.008, 0.009, 0.0095, 0.0099, 0.01, 0.0101, 0.011, 0.012]

    print(f"\nStress response at different strains:")
    for eps in test_strains:
        stress = brittle_elastic.get_stress(eps)
        tangent = brittle_elastic.get_tangent(eps)
        print(f"  eps = {eps:.4f}: stress = {stress:.1f} MPa, tangent = {tangent:.1f} MPa")

    # What happens with negative strain (compression)?
    print(f"\nNegative strain (compression) behavior:")
    for eps in [-0.001, -0.005, -0.01]:
        stress = brittle_elastic.get_stress(eps)
        print(f"  eps = {eps:.4f}: stress = {stress:.1f} MPa")

    # Plot the constitutive law
    fig, ax = plt.subplots(figsize=(10, 6))

    eps_range = np.linspace(-0.005, 0.015, 200)
    stress_range = [brittle_elastic.get_stress(e) for e in eps_range]

    ax.plot(eps_range * 1000, stress_range, 'b-', linewidth=2)
    ax.axvline(x=epsuk * 1000, color='r', linestyle='--', label=f'eps_u = {epsuk * 1000:.1f}‰')
    ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
    ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    ax.set_xlabel('Strain ε [‰]')
    ax.set_ylabel('Stress σ [MPa]')
    ax.set_title('CFRP Reinforcement Constitutive Law (Elastic with eps_u limit)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('constitutive_law_behavior.png', dpi=150)
    print("\nSaved constitutive law plot to: constitutive_law_behavior.png")
    plt.show()


def investigate_concrete_strains():
    """
    Check if the concrete strains at cracking are within valid limits.
    The issue might be extreme compression at the top of the section.
    """

    print("\n" + "=" * 70)
    print("CONCRETE STRAIN INVESTIGATION")
    print("=" * 70)

    # Get concrete properties
    fck = 30.0
    concrete = create_concrete(
        fck=fck,
        constitutive_law='parabolarectangle',
        alpha_cc=0.85,
        gamma_c=1.5
    )

    eps_c1 = concrete.eps_c1  # Strain at peak stress
    eps_cu1 = concrete.eps_cu1  # Ultimate strain
    Ecm = concrete.Ecm
    fctm = concrete.fctm
    eps_ctm = fctm / Ecm

    print(f"\nConcrete C{fck} strain limits:")
    print(f"  eps_ctm (cracking) = {eps_ctm:.6f} ({eps_ctm * 1000:.3f}‰)")
    print(f"  eps_c1 (peak stress) = {eps_c1:.6f} ({eps_c1 * 1000:.3f}‰)")
    print(f"  eps_cu1 (ultimate) = {eps_cu1:.6f} ({eps_cu1 * 1000:.3f}‰)")

    # Now check what strains we get at the top for different prestress levels
    print(f"\n{'Factor':<10} {'eps_top':<15} {'eps_top [‰]':<12} {'Exceeds eps_cu1?'}")
    print("-" * 60)

    factors = [0.35, 0.38, 0.39, 0.392, 0.393, 0.40, 0.45]

    for f in factors:
        r = analyze_prestress_effect(f, verbose=False)
        eps_top = r['eps_top']

        if np.isnan(eps_top):
            status = "CALC FAILED"
        elif eps_top < eps_cu1:  # eps_cu1 is negative
            status = f"YES! ({eps_top / eps_cu1:.1f}x limit)"
        else:
            status = "No"

        print(f"{f:<10.3f} {eps_top:<15.6f} {eps_top * 1000:<12.3f} {status}")

    print(f"\n[KEY INSIGHT]")
    print(f"  The HP shell section is very deep (zmax = 545 mm from bottom).")
    print(f"  At cracking (bottom fiber at eps_ctm), the strain at the top can be extreme.")
    print(f"  If eps_top exceeds the concrete ultimate strain, the calculation becomes invalid.")


def check_reinf_strain_at_cracking():
    """
    Calculate what the total reinforcement strain would be at cracking
    for different prestress levels, and check if it exceeds eps_u.
    """

    print("\n" + "=" * 70)
    print("REINFORCEMENT STRAIN CHECK AT CRACKING")
    print("=" * 70)

    epsuk = 0.01  # Ultimate strain

    # For a range of prestress factors
    factors = np.linspace(0.30, 0.50, 21)

    print(
        f"\n{'Factor':<10} {'Init Strain':<15} {'Bend Strain':<15} {'Total Strain':<15} {'% of epsuk':<12} {'Status'}")
    print("-" * 80)

    for f in factors:
        r = analyze_prestress_effect(f, verbose=False)

        init = r['initial_strain']
        bend = r['eps_reinf_bending']
        total = r['eps_reinf_total']
        pct = (total / epsuk) * 100 if not np.isnan(total) else np.nan

        if np.isnan(total):
            status = "CALC FAILED"
        elif total > epsuk:
            status = "EXCEEDS eps_u!"
        elif total > 0.95 * epsuk:
            status = "NEAR LIMIT"
        else:
            status = "OK"

        print(f"{f:<10.3f} {init:<15.6f} {bend:<15.6f} {total:<15.6f} {pct:<12.1f} {status}")

    print(f"\n[NOTE]")
    print(f"  eps_u = {epsuk}")
    print(f"  When total strain > eps_u, the constitutive law may return 0 stress,")
    print(f"  causing the equilibrium calculation to fail or find wrong solutions.")


if __name__ == "__main__":
    # First, check the constitutive law behavior
    investigate_constitutive_law()

    # Check concrete strains at cracking
    investigate_concrete_strains()

    # Check reinforcement strain at cracking
    check_reinf_strain_at_cracking()

    # Run the scan
    results_coarse, results_fine = scan_prestress_range()

    # Deep investigation at threshold
    r_below, r_above = investigate_threshold()

    # Plot comparison
    plot_comparison(factor_ok=0.35, factor_bad=0.40)