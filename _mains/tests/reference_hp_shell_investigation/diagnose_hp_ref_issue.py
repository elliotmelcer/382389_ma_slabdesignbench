"""
Diagnostic script to investigate why test_slab_construction_ref
gives incorrect bending strength results.

The issue: structuralcodes calculate_bending_strength returns a strain profile
where the entire section is in compression, which is physically impossible
for a section under pure bending (N=0).

Expected (INCA2): top=-3.5‰, bottom=+4.978‰, M_u≈103 kNm
Got (your code):  top=-3.5‰, bottom=-0.568‰ (both compression!)
"""

import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt

from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic

set_design_code('ec2_2004')

# Import the HP geometry classes
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell

# Import testing materials
from _mains.testing_files.testing_materials import (
    concrete_c50_uls, solidian_Q85_pre_37
)
from _mains.testing_files.testing_hp_sections import hp_ref

from core.analysis_core.section_methods import (
    calculate_bending_strength_uls_Nmm,
    get_strain_at_point
)
from core.visualization_core.visualization import plot_cross_section


def diagnose_hp_ref():
    """
    Diagnose the hp_ref section behavior.
    """
    print("=" * 70)
    print("DIAGNOSING HP_REF BENDING STRENGTH ISSUE")
    print("=" * 70)

    # Create the hp_shell and section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)

    # Get section extents
    _, _, zmin, zmax = section.geometry.calculate_extents()

    print(f"\n[1] GEOMETRY PARAMETERS")
    print(f"    B = {hp_ref.B} mm")
    print(f"    L = {hp_ref.L} mm")
    print(f"    Hx = {hp_ref.Hx} mm")
    print(f"    Hy = {hp_ref.Hy} mm")
    print(f"    t = {hp_ref.t} mm")
    print(f"    dy = {hp_ref.dy} mm  <-- THIS IS LARGE!")
    print(f"    nt = {hp_ref.nt}")

    print(f"\n[2] DERIVED GEOMETRY")
    print(f"    x_p = {hp_ref.x_p():.2f} mm")
    print(f"    y_p = {hp_ref.y_p():.2f} mm")
    print(f"    z_p = {hp_ref.z_p():.2f} mm")
    print(f"    alpha_edge = {hp_ref.alpha_edge():.4f}")
    print(f"    alpha_edge_bar = {hp_ref.alpha_edge_bar():.4f}")

    print(f"\n[3] SECTION EXTENTS (at midspan)")
    print(f"    zmin = {zmin:.2f} mm (bottom of section)")
    print(f"    zmax = {zmax:.2f} mm (top of section)")
    print(f"    depth = {zmax - zmin:.2f} mm")

    # Get reinforcement positions
    print(f"\n[4] REINFORCEMENT POSITIONS")
    point_geoms = section.geometry.point_geometries
    z_reinf = [pg.point.y for pg in point_geoms]
    z_reinf_min = min(z_reinf)
    z_reinf_max = max(z_reinf)
    z_reinf_avg = np.mean(z_reinf)

    print(f"    Number of point geometries: {len(point_geoms)}")
    print(f"    z_reinf min = {z_reinf_min:.2f} mm")
    print(f"    z_reinf max = {z_reinf_max:.2f} mm")
    print(f"    z_reinf avg = {z_reinf_avg:.2f} mm")
    print(f"    Distance from bottom: {z_reinf_min - zmin:.2f} to {z_reinf_max - zmin:.2f} mm")
    print(f"    Relative depth: {(z_reinf_avg - zmin) / (zmax - zmin) * 100:.1f}% from bottom")

    # Get prestress info
    reinf_material = point_geoms[0].material
    initial_strain = getattr(reinf_material, 'initial_strain', 0)
    print(f"\n[5] REINFORCEMENT PROPERTIES")
    print(f"    Initial strain (prestress): {initial_strain * 1000:.3f}‰")
    print(f"    Es = {reinf_material.Es:.0f} MPa")

    # Now calculate bending strength
    print(f"\n[6] CALCULATING BENDING STRENGTH...")
    result = calculate_bending_strength_uls_Nmm(section, n=0)

    m_u = result['m_u']
    strain_profile = result['strain_profile']
    eps_0, chi_y, chi_z = strain_profile

    eps_top = get_strain_at_point(strain_profile, 0, zmax)
    eps_bot = get_strain_at_point(strain_profile, 0, zmin)

    print(f"\n[7] RESULTS FROM calculate_bending_strength_uls_Nmm")
    print(f"    M_u = {m_u / 1e6:.2f} kNm")
    print(f"    eps_0 = {eps_0:.6f}")
    print(f"    chi_y = {chi_y:.9f} 1/mm")
    print(f"    chi_z = {chi_z}")

    print(f"\n[8] STRAIN PROFILE CHECK")
    print(f"    eps(zmin) = eps_bot = {eps_bot * 1000:.3f}‰")
    print(f"    eps(zmax) = eps_top = {eps_top * 1000:.3f}‰")

    # Calculate reinforcement strains
    print(f"\n[9] REINFORCEMENT STRAINS")
    for i, z_s in enumerate(z_reinf[:5]):  # Show first 5
        eps_bending = eps_0 + chi_y * z_s
        eps_total = initial_strain + eps_bending
        print(
            f"    Rebar {i + 1}: z={z_s:.1f}mm, eps_bending={eps_bending * 1000:.3f}‰, eps_total={eps_total * 1000:.3f}‰")

    # Sanity checks
    print(f"\n[10] SANITY CHECKS")

    if eps_top < 0 and eps_bot < 0:
        print(f"    ❌ ENTIRE SECTION IN COMPRESSION - THIS IS WRONG!")
        print(f"    For N=0, we need tension somewhere to balance compression.")
    elif eps_top < 0 and eps_bot > 0:
        print(f"    ✓ Normal bending: top in compression, bottom in tension")
    else:
        print(f"    ? Unusual strain distribution")

    if chi_y > 0:
        print(f"    ⚠️  chi_y is POSITIVE (hogging curvature)")
        print(f"       For sagging bending, chi_y should be NEGATIVE")
    else:
        print(f"    ✓ chi_y is negative (sagging curvature)")

    # What SHOULD the result be (based on INCA2)?
    print(f"\n[11] EXPECTED VALUES (from INCA2)")
    print(f"    eps_top (expected) = -3.5‰")
    print(f"    eps_bot (expected) = +4.978‰")
    print(f"    M_u (expected) ≈ 103 kNm")

    # Calculate what chi_y should be for INCA2 results
    chi_y_expected = (-0.0035 - 0.004978) / (zmax - zmin)
    eps_0_expected = 0.004978 - chi_y_expected * zmin

    print(f"\n[12] EXPECTED STRAIN PROFILE")
    print(f"    chi_y_expected = {chi_y_expected:.9f} 1/mm")
    print(f"    eps_0_expected = {eps_0_expected:.6f}")

    print(f"\n[13] COMPARISON")
    print(f"    chi_y ratio (got/expected) = {chi_y / chi_y_expected:.3f}")
    print(f"    Your chi_y is {chi_y / chi_y_expected:.1%} of the expected value!")

    # Plot the section
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot cross-section
    plot_cross_section(section, ax=axes[0])
    axes[0].set_title("HP-Ref Section at Midspan\n(Note reinforcement positions)")

    # Plot strain profile comparison
    ax2 = axes[1]

    # Your result
    z_plot = np.linspace(zmin, zmax, 100)
    eps_your = eps_0 + chi_y * z_plot
    ax2.plot(eps_your * 1000, z_plot, 'r-', linewidth=2, label='Your result')

    # Expected (INCA2)
    eps_expected = eps_0_expected + chi_y_expected * z_plot
    ax2.plot(eps_expected * 1000, z_plot, 'g--', linewidth=2, label='INCA2 expected')

    # Mark key points
    ax2.axhline(zmin, color='gray', linestyle=':', alpha=0.5)
    ax2.axhline(zmax, color='gray', linestyle=':', alpha=0.5)
    ax2.axvline(0, color='black', linewidth=0.5)

    # Mark reinforcement level
    ax2.axhline(z_reinf_avg, color='blue', linestyle='--', alpha=0.5, label=f'Avg reinf z={z_reinf_avg:.1f}mm')

    ax2.set_xlabel('Strain [‰]')
    ax2.set_ylabel('z [mm]')
    ax2.set_title('Strain Profile Comparison')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(r"C:\Users\LJ\Downloads\hp_ref_diagnosis.png", dpi=150)
    print(f"\n[PLOT SAVED] /mnt/user-data/outputs/hp_ref_diagnosis.png")

    return result


def suggest_fix():
    """
    Suggest potential fixes for the issue.
    """
    print("\n" + "=" * 70)
    print("POTENTIAL CAUSES AND FIXES")
    print("=" * 70)

    print("""
The issue is that structuralcodes' calculate_bending_strength is finding
a strain profile where the entire section is in compression, which violates
equilibrium for N=0.

LIKELY CAUSES:

1. ALGORITHM ISSUE: The bending strength algorithm may be converging to 
   a local extremum instead of the global maximum. This can happen when:
   - Reinforcement is highly concentrated at one depth
   - The section shape is unusual (arch-like)

2. SEARCH BOUNDS: The algorithm's search space for curvature (chi_y) may
   not include the physically correct range.

3. PRESTRESS EFFECT: The initial strain in the reinforcement creates a
   prestress force. If not properly accounted for, this can affect the
   equilibrium search.

SUGGESTED FIXES:

1. MANUAL ITERATION: Instead of using calculate_bending_strength directly,
   implement your own iteration that:
   - Fixes eps_top = -3.5‰ (concrete crushing strain)
   - Varies chi_y from a physically meaningful range
   - Finds N=0 equilibrium
   - Returns the corresponding moment

2. CHECK CURVATURE BOUNDS: Verify that the curvature search includes
   the expected value of chi_y ≈ -2.3e-5 /mm

3. COMPARE WITH hp_c1_1: Run the same analysis on hp_c1_1 and compare
   the internal state of the algorithm to see where it diverges.

4. CHECK structuralcodes VERSION: There may be known issues with
   certain geometries or reinforcement configurations.
""")


if __name__ == "__main__":
    diagnose_hp_ref()
    suggest_fix()