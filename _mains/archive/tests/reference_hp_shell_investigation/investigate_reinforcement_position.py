"""
Investigate reinforcement positions in hp_ref section.

The issue: At INCA2-like strain profile (eps_bot = +5‰), we get N = +3.6 MN
But INCA2 achieves N = 0 at that strain profile.

This suggests either:
1. Reinforcement is positioned differently in INCA2
2. Section geometry differs
3. Prestress is handled differently
"""

import numpy as np
import matplotlib.pyplot as plt
from structuralcodes import set_design_code

set_design_code('ec2_2004')

from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.hp_model.hp_geometry import HPGeometry
from _mains.testing_files.testing_materials import concrete_c50_uls, ref_solidian_Q85_pre_37
from _mains.testing_files.testing_hp_sections import hp_ref

from core.visualization_core.visualization import plot_cross_section


def investigate_reinforcement_positions():
    """
    Investigate where the reinforcement is positioned relative to the section.
    """
    print("=" * 70)
    print("INVESTIGATING REINFORCEMENT POSITIONS IN HP_REF")
    print("=" * 70)

    # Create section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)

    # Get section extents
    _, _, zmin, zmax = section.geometry.calculate_extents()
    depth = zmax - zmin

    print(f"\n[1] SECTION EXTENTS")
    print(f"    zmin = {zmin:.2f} mm")
    print(f"    zmax = {zmax:.2f} mm")
    print(f"    depth = {depth:.2f} mm")

    # Get reinforcement positions
    print(f"\n[2] REINFORCEMENT POSITIONS")
    point_geoms = section.geometry.point_geometries

    # Group by unique z-coordinate (approximately)
    z_coords = [(pg.point.x, pg.point.y) for pg in point_geoms]  # (y, z) in section coords

    print(f"    Total rebars: {len(point_geoms)}")
    print(f"\n    Individual positions (y, z):")

    unique_z = set()
    for i, (y, z) in enumerate(z_coords):
        print(f"      Rebar {i + 1:2d}: y = {y:+8.2f} mm, z = {z:+8.2f} mm")
        unique_z.add(round(z, 1))

    print(f"\n    Unique z-levels: {sorted(unique_z)}")

    # Compute effective depth
    z_reinf = [z for (y, z) in z_coords]
    z_reinf_avg = np.mean(z_reinf)
    d_eff = zmax - z_reinf_avg  # Effective depth from top to reinforcement centroid

    print(f"\n[3] EFFECTIVE DEPTH")
    print(f"    Average reinforcement z = {z_reinf_avg:.2f} mm")
    print(f"    Effective depth d = {d_eff:.2f} mm (from top to reinforcement)")
    print(f"    Effective depth ratio d/h = {d_eff / depth * 100:.1f}%")

    # Check alpha values
    print(f"\n[4] TENDON ALPHA VALUES (from HP geometry)")
    print(f"    alpha_edge = {hp_ref.alpha_edge():.4f}")
    print(f"    alpha_edge_bar = {hp_ref.alpha_edge_bar():.4f}")
    print(f"    alpha range = {hp_ref.alpha_edge():.4f} to {hp_ref.alpha_edge_bar():.4f}")
    print(f"    (For reference: alpha = 0.5 is the center/bottom of the arch)")

    alpha_list = hp_ref.alpha_list()
    print(f"    Individual alphas: {[f'{a:.4f}' for a in alpha_list]}")

    # Check tendon coordinates at midspan
    print(f"\n[5] TENDON COORDINATES AT MIDSPAN (x=0)")
    tendon_coords = hp_ref.tendon_coords_at_x(0.0)  # x=0 is midspan in internal coords

    print(f"    Number of tendons: {len(tendon_coords)}")
    y_tendons = [c[0] for c in tendon_coords]
    z_tendons = [c[1] for c in tendon_coords]

    print(f"    y range: {min(y_tendons):.2f} to {max(y_tendons):.2f} mm")
    print(f"    z range: {min(z_tendons):.2f} to {max(z_tendons):.2f} mm")

    # THE KEY QUESTION: Where should tendons be for good bending capacity?
    print(f"\n[6] ANALYSIS: REINFORCEMENT POSITION PROBLEM")
    print(f"    For maximum sagging moment capacity, reinforcement should be")
    print(f"    near the BOTTOM of the section (tension zone).")
    print(f"")
    print(f"    Current situation:")
    print(f"      - Section bottom: z = {zmin:.2f} mm")
    print(f"      - Reinforcement:  z = {min(z_reinf):.2f} to {max(z_reinf):.2f} mm")
    print(f"      - Distance from bottom: {min(z_reinf) - zmin:.2f} mm")
    print(f"")

    if min(z_reinf) - zmin > 20:
        print(f"    ⚠️  Reinforcement is {min(z_reinf) - zmin:.1f} mm above section bottom!")
        print(f"       This reduces moment arm significantly.")

    # Compare with what a typical section would have
    print(f"\n[7] COMPARISON WITH TYPICAL DESIGN")
    typical_cover = 25  # mm
    typical_d = zmax - zmin - typical_cover
    print(f"    With {typical_cover} mm cover, effective depth would be {typical_d:.1f} mm")
    print(f"    Current effective depth: {d_eff:.1f} mm")
    print(f"    Difference: {typical_d - d_eff:.1f} mm ({(typical_d - d_eff) / typical_d * 100:.1f}% reduction)")

    # Visualize
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))

    # Plot 1: Cross-section with reinforcement highlighted
    ax1 = axes[0]
    plot_cross_section(section, ax=ax1)
    ax1.axhline(z_reinf_avg, color='red', linestyle='--', linewidth=2,
                label=f'Reinforcement centroid (z={z_reinf_avg:.1f}mm)')
    ax1.axhline(zmin, color='blue', linestyle=':', linewidth=1, label=f'Section bottom (z={zmin:.1f}mm)')
    ax1.axhline(zmax, color='green', linestyle=':', linewidth=1, label=f'Section top (z={zmax:.1f}mm)')
    ax1.legend(loc='upper right')
    ax1.set_title("HP-Ref Section at Midspan\nNote: Reinforcement is very close to section bottom")

    # Plot 2: Reinforcement y-z positions
    ax2 = axes[1]
    ax2.scatter(y_tendons, z_tendons, s=100, c='red', label='Reinforcement')
    ax2.axhline(zmin, color='blue', linestyle=':', label='Section bottom')
    ax2.axhline(zmax, color='green', linestyle=':', label='Section top')
    ax2.axhline(z_reinf_avg, color='red', linestyle='--', alpha=0.5)

    # Draw section outline (approximate)
    y_outline = np.linspace(-600, 600, 100)
    z_mid = [hp_ref._z(0, y) for y in y_outline]
    z_bot = [z - hp_ref.t / 2 for z in z_mid]
    z_top = [z + hp_ref.t / 2 for z in z_mid]

    ax2.plot(y_outline, z_bot, 'b-', linewidth=1, alpha=0.5)
    ax2.plot(y_outline, z_top, 'g-', linewidth=1, alpha=0.5)
    ax2.fill_between(y_outline, z_bot, z_top, alpha=0.1, color='gray')

    ax2.set_xlabel('y [mm]')
    ax2.set_ylabel('z [mm]')
    ax2.set_title('Reinforcement Layout in Section')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')

    plt.tight_layout()
    plt.savefig('hp_ref_reinforcement_investigation.png', dpi=150)
    print(f"\n[PLOT SAVED] hp_ref_reinforcement_investigation.png")
    plt.show()

    # Key question for user
    print("\n" + "=" * 70)
    print("QUESTION FOR INCA2 COMPARISON")
    print("=" * 70)
    print("""
In INCA2, how did you define the reinforcement position?

In your code:
- Reinforcement is on the HP SURFACE (mid-plane of the shell)
- At midspan, this places rebars at z ≈ 0-6 mm
- This is 22-28 mm ABOVE the section bottom (zmin = -22.5 mm)

For a typical prestressed section:
- Reinforcement should be near the BOTTOM fiber
- With ~25 mm cover, it would be at z ≈ zmin + 25 = +2.5 mm

The issue might be that the tendon z-coordinates follow the HP surface
equation (z = y²/b² - x²/a²) rather than being at a fixed depth from
the bottom surface.

Please check in INCA2:
1. Where is the reinforcement positioned? (z-coordinate)
2. What is the effective depth from compression fiber to reinforcement?
""")

    return section, z_coords


def check_equilibrium_at_different_reinf_positions():
    """
    What if reinforcement was at a different z-coordinate?
    """
    print("\n" + "=" * 70)
    print("SENSITIVITY: EQUILIBRIUM VS REINFORCEMENT POSITION")
    print("=" * 70)

    from copy import deepcopy

    # Create base section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)

    _, _, zmin, zmax = section.geometry.calculate_extents()
    depth = zmax - zmin

    # Current reinforcement position
    point_geoms = section.geometry.point_geometries
    z_reinf_current = np.mean([pg.point.y for pg in point_geoms])

    print(f"Current reinforcement z = {z_reinf_current:.2f} mm")
    print(f"Section bottom = {zmin:.2f} mm")
    print(f"Section top = {zmax:.2f} mm")

    # What strain profile would give eps_bot = +5‰?
    eps_top = -0.0035
    eps_bot_target = 0.005
    chi_y_needed = (eps_top - eps_bot_target) / depth
    eps_0_needed = eps_bot_target - chi_y_needed * zmin

    print(f"\nFor INCA2-like strain profile (eps_bot = +5‰):")
    print(f"  chi_y needed = {chi_y_needed:.6e} 1/mm")
    print(f"  eps_0 needed = {eps_0_needed:.6f}")

    # At current reinforcement position
    eps_reinf_bending = eps_0_needed + chi_y_needed * z_reinf_current
    initial_strain = 0.004504
    eps_reinf_total = initial_strain + eps_reinf_bending

    print(f"\nAt current reinforcement z = {z_reinf_current:.2f}:")
    print(f"  eps_bending = {eps_reinf_bending * 1000:.3f}‰")
    print(f"  eps_total = {eps_reinf_total * 1000:.3f}‰")

    # Calculate reinforcement force
    A_s = 22 * 85  # mm²
    Es = 230000  # MPa
    F_s = A_s * Es * eps_reinf_total / 1000  # kN
    print(f"  Reinforcement tension = {F_s:.0f} kN = {F_s / 1000:.2f} MN")

    print("\nThis large tension force (~4 MN) cannot be balanced by")
    print("concrete compression with the current section geometry.")


if __name__ == "__main__":
    investigate_reinforcement_positions()
    check_equilibrium_at_different_reinf_positions()