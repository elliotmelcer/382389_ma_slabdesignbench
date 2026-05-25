"""
Diagnostic: Why does concrete not provide enough compression?

At INCA2 strain profile (eps_top=-3.5‰, eps_bot=+5‰):
- Reinforcement tension ≈ 4 MN (correct for CFRP)
- Concrete compression should ≈ 4 MN (for N=0)
- But Python computes only ~0.4 MN compression!

This script investigates the concrete stress integration.
"""

import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from structuralcodes import set_design_code

set_design_code('ec2_2004')

from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from _mains.testing_files.testing_materials import concrete_c50_uls, ref_solidian_Q85_pre_37
from _mains.testing_files.testing_hp_sections import hp_ref

from core.analysis_core.section_methods import get_strain_at_point


def diagnose_concrete_compression():
    """
    Check concrete compression at INCA2-like strain profile.
    """
    print("=" * 70)
    print("DIAGNOSING CONCRETE COMPRESSION FORCE")
    print("=" * 70)

    # Create section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)
    analysis_section = deepcopy(section)

    # Get section extents
    _, _, zmin, zmax = section.geometry.calculate_extents()
    depth = zmax - zmin

    print(f"\n[1] SECTION GEOMETRY")
    print(f"    zmin = {zmin:.2f} mm")
    print(f"    zmax = {zmax:.2f} mm")
    print(f"    depth = {depth:.2f} mm")

    # INCA2 strain profile
    eps_top = -0.0035
    eps_bot = 0.004978
    chi_y_inca = (eps_top - eps_bot) / depth
    eps_0_inca = eps_bot - chi_y_inca * zmin
    strain_profile_inca = [eps_0_inca, chi_y_inca, 0.0]

    print(f"\n[2] INCA2 STRAIN PROFILE")
    print(f"    eps_top = {eps_top * 1000:.3f}‰")
    print(f"    eps_bot = {eps_bot * 1000:.3f}‰")
    print(f"    chi_y = {chi_y_inca:.6e} 1/mm")
    print(f"    eps_0 = {eps_0_inca:.6f}")

    # Neutral axis position
    z_neutral = zmin + (0 - eps_bot) / (eps_top - eps_bot) * depth
    print(f"\n[3] NEUTRAL AXIS")
    print(f"    z_neutral = {z_neutral:.2f} mm")
    print(f"    Compression zone depth = {zmax - z_neutral:.2f} mm")
    print(f"    Tension zone depth = {z_neutral - zmin:.2f} mm")

    # Get calculator
    calculator = analysis_section.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    # Integrate forces at INCA2 strain profile
    print(f"\n[4] STRESS INTEGRATION AT INCA2 PROFILE")
    N, My, Mz, _ = calculator.integrator.integrate_strain_response_on_geometry(
        analysis_section.geometry,
        strain_profile_inca,
        integration_data=integration_data,
        mesh_size=mesh_size
    )

    print(f"    N = {N / 1e6:+.3f} MN")
    print(f"    M = {My / 1e6:+.3f} kNm")

    # Compute reinforcement contribution separately
    print(f"\n[5] REINFORCEMENT FORCE")
    point_geoms = section.geometry.point_geometries
    initial_strain = 0.37 * 12.17 / 1000  # 37% of eps_uk for Q85

    total_reinf_force = 0
    for pg in point_geoms:
        z_s = pg.point.y
        eps_bending = eps_0_inca + chi_y_inca * z_s
        eps_total = initial_strain + eps_bending

        # Get stress from constitutive law
        stress = pg.material.constitutive_law.get_stress(eps_total)
        force = pg.area * stress
        total_reinf_force += force

    print(f"    Initial strain = {initial_strain * 1000:.3f}‰")
    print(f"    Total reinforcement force = {total_reinf_force / 1e6:+.3f} MN")

    # Implied concrete force
    concrete_force = N - total_reinf_force
    print(f"\n[6] IMPLIED CONCRETE FORCE")
    print(f"    Concrete force = N - F_reinf = {concrete_force / 1e6:+.3f} MN")

    # Expected concrete force for equilibrium
    print(f"\n[7] EQUILIBRIUM CHECK")
    print(f"    For N = 0, need concrete force = {-total_reinf_force / 1e6:+.3f} MN")
    print(f"    Actual concrete force = {concrete_force / 1e6:+.3f} MN")
    print(f"    Deficit = {(-total_reinf_force - concrete_force) / 1e6:.3f} MN")

    # Check concrete material properties
    print(f"\n[8] CONCRETE MATERIAL PROPERTIES")
    conc = None
    for geo in section.geometry.geometries:
        if hasattr(geo, 'material'):
            conc = geo.material
            break

    if conc:
        print(f"    fck = {conc.fck} MPa")
        print(f"    Ecm = {conc.Ecm} MPa")
        print(f"    Constitutive law: {conc.constitutive_law}")

        # Check stress at key strains
        print(f"\n    Stress at key strains:")
        for eps in [-0.0035, -0.002, -0.001, 0.0]:
            sig = conc.constitutive_law.get_stress(eps)
            print(f"      eps = {eps * 1000:+.2f}‰ → sigma = {sig:+.2f} MPa")

    # Check section area
    print(f"\n[9] SECTION AREA CHECK")
    # Get polygon area
    for geo in section.geometry.geometries:
        if hasattr(geo, 'polygon'):
            area = geo.polygon.area
            print(f"    Concrete polygon area = {area:.0f} mm²")

            # Estimate compression zone area (above neutral axis)
            from shapely.geometry import box
            clip_box = box(-1000, z_neutral, 1000, zmax + 100)
            compression_zone = geo.polygon.intersection(clip_box)
            if not compression_zone.is_empty:
                print(f"    Compression zone area = {compression_zone.area:.0f} mm²")

                # Estimate max compression force
                fcd = 0.85 * 50 / 1.5  # Approximate fcd
                max_compression = compression_zone.area * fcd / 1e6
                print(f"    Max possible compression (fcd={fcd:.1f}MPa) = {max_compression:.2f} MN")

    # What does INCA2 report for concrete compression?
    print(f"\n" + "=" * 70)
    print("QUESTION FOR INCA2:")
    print("=" * 70)
    print(f"""
At the ultimate state (eps_top=-3.5‰, eps_bot=+4.978‰), what does INCA2 report for:

1. Total axial force N = ?
2. Concrete compression force = ?
3. Reinforcement tension force = ?
4. Compression zone area = ?

In Python:
- Total N = {N / 1e6:+.3f} MN (should be 0 for equilibrium)
- Reinforcement tension = {total_reinf_force / 1e6:+.3f} MN  
- Implied concrete compression = {concrete_force / 1e6:+.3f} MN

The Python code is getting only {abs(concrete_force) / 1e6:.2f} MN compression,
but needs {abs(total_reinf_force) / 1e6:.2f} MN to achieve equilibrium.
""")

    return N, total_reinf_force, concrete_force


def check_section_area_vs_inca():
    """
    Compare section areas with what INCA2 might have.
    """
    print("\n" + "=" * 70)
    print("SECTION AREA COMPARISON")
    print("=" * 70)

    # HP geometry parameters
    B = 1200  # mm
    L = 8000  # mm
    Hx = 80  # mm
    Hy = 320  # mm
    t = 45  # mm

    # Compute section at midspan analytically
    b = B / (2 * np.sqrt(Hy))  # = 33.54

    print(f"\n[1] HP PARAMETERS")
    print(f"    B = {B} mm")
    print(f"    L = {L} mm")
    print(f"    Hx = {Hx} mm")
    print(f"    Hy = {Hy} mm")
    print(f"    t = {t} mm")
    print(f"    b = B/(2√Hy) = {b:.2f}")

    # At midspan (x=0), z = y²/b²
    # Section goes from y = -B/2 to y = +B/2
    y_vals = np.linspace(-B / 2, B / 2, 1000)
    z_mid = y_vals ** 2 / b ** 2

    print(f"\n[2] SECTION EXTENT AT MIDSPAN")
    print(f"    z at y=0: {0} mm")
    print(f"    z at y=±{B / 2}: {(B / 2) ** 2 / b ** 2:.2f} mm")

    # Approximate section area (integrating arc length * thickness)
    # More accurate: use the polygon area
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)

    for geo in section.geometry.geometries:
        if hasattr(geo, 'polygon'):
            area = geo.polygon.area
            print(f"\n[3] POLYGON AREA FROM CODE")
            print(f"    Area = {area:.0f} mm²")

            # Compare with simple estimate
            simple_area = B * t  # If it were a flat plate
            print(f"    Simple estimate (B×t) = {simple_area:.0f} mm²")
            print(f"    Ratio = {area / simple_area:.2f}")

            # Arc length estimate
            # Arc length of parabola y²/b² from y=-B/2 to y=+B/2
            # s = integral of sqrt(1 + (dz/dy)²) dy = integral of sqrt(1 + (2y/b²)²) dy
            arc_length = 0
            for i in range(len(y_vals) - 1):
                dy = y_vals[i + 1] - y_vals[i]
                y_mid = (y_vals[i] + y_vals[i + 1]) / 2
                dz_dy = 2 * y_mid / b ** 2
                ds = np.sqrt(1 + dz_dy ** 2) * dy
                arc_length += ds

            arc_area = arc_length * t
            print(f"\n[4] ARC LENGTH ESTIMATE")
            print(f"    Arc length = {arc_length:.0f} mm")
            print(f"    Arc area (arc_length × t) = {arc_area:.0f} mm²")
            print(f"    Polygon area / Arc area = {area / arc_area:.3f}")


if __name__ == "__main__":
    diagnose_concrete_compression()
    check_section_area_vs_inca()