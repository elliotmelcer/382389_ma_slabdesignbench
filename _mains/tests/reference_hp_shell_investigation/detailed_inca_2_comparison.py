"""
Direct comparison with INCA2 results.

INCA2 at ultimate state:
- M.y = 100.64 kNm
- N = 0.0009 kN ≈ 0
- chi = 23.6774 ‰/m = 2.3677e-5 1/mm
- eps.0 = 4.4452‰ (strain at origin)
- eps_top = -3.5‰
- eps_bot = +4.978‰
- sigma_concrete = -28.33 MPa (fcd)
- sigma_reinf = 2027-2058 MPa

Python at same strain profile shows N = +3.6 MN!
This script investigates why.
"""

import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
from structuralcodes import set_design_code

set_design_code('ec2_2004')

from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from _mains.testing_files.testing_materials import concrete_c50_uls, ref_solidian_Q85_pre_37
from _mains.testing_files.testing_hp_sections import hp_ref


def detailed_inca2_comparison():
    """
    Compare Python integration with INCA2 at the exact same strain profile.
    """
    print("=" * 80)
    print("DETAILED COMPARISON WITH INCA2")
    print("=" * 80)

    # Create section
    hp_shell = HPShell(hp_ref, concrete_c50_uls, ref_solidian_Q85_pre_37, reinf_area=85)
    section = hp_shell.section_at(0.5)
    analysis_section = deepcopy(section)

    # Get section extents
    _, _, zmin, zmax = section.geometry.calculate_extents()
    depth = zmax - zmin

    print(f"\n[1] SECTION GEOMETRY (Python)")
    print(f"    zmin = {zmin:.2f} mm")
    print(f"    zmax = {zmax:.2f} mm")
    print(f"    depth = {depth:.2f} mm")

    # INCA2 strain profile values
    eps_top_inca = -0.0035
    eps_bot_inca = 0.004978
    chi_y_inca = -23.6774e-6  # Negative for sagging (sign convention)

    # Calculate eps_0 for INCA2 profile
    # eps_bot = eps_0 + chi_y * zmin
    eps_0_inca = eps_bot_inca - chi_y_inca * zmin

    strain_profile_inca = [eps_0_inca, chi_y_inca, 0.0]

    # Verify strain profile
    eps_top_check = eps_0_inca + chi_y_inca * zmax
    eps_bot_check = eps_0_inca + chi_y_inca * zmin

    print(f"\n[2] INCA2 STRAIN PROFILE (reconstructed)")
    print(f"    chi_y = {chi_y_inca:.6e} 1/mm")
    print(f"    eps_0 = {eps_0_inca * 1000:.4f}‰")
    print(f"    eps_top (check) = {eps_top_check * 1000:.4f}‰ (INCA2: -3.5‰)")
    print(f"    eps_bot (check) = {eps_bot_check * 1000:.4f}‰ (INCA2: +4.978‰)")

    # Neutral axis
    z_neutral = -eps_0_inca / chi_y_inca
    print(f"    z_neutral = {z_neutral:.2f} mm")
    print(f"    Compression zone: {z_neutral:.1f} to {zmax:.1f} mm (depth = {zmax - z_neutral:.1f} mm)")

    # Get calculator
    calculator = analysis_section.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    # Integrate at INCA2 strain profile
    print(f"\n[3] PYTHON INTEGRATION AT INCA2 STRAIN PROFILE")
    N_total, My_total, Mz_total, _ = calculator.integrator.integrate_strain_response_on_geometry(
        analysis_section.geometry,
        strain_profile_inca,
        integration_data=integration_data,
        mesh_size=mesh_size
    )

    print(f"    N_total = {N_total / 1e6:+.4f} MN (INCA2: ≈0)")
    print(f"    M_total = {My_total / 1e6:+.4f} kNm (INCA2: 100.64 kNm)")

    # ================================================================
    # SEPARATE CONCRETE AND REINFORCEMENT CONTRIBUTIONS
    # ================================================================
    print(f"\n[4] DETAILED FORCE BREAKDOWN")

    # --- Reinforcement contribution ---
    print(f"\n    [4a] REINFORCEMENT")
    point_geoms = section.geometry.point_geometries

    # Q85 prestress: 37% of eps_uk = 0.37 * 12.17‰ = 4.503‰
    initial_strain = ref_solidian_Q85_pre_37.initial_strain
    Es = ref_solidian_Q85_pre_37.Es

    print(f"         Initial strain = {initial_strain * 1000:.3f}‰")
    print(f"         Es = {Es:.0f} MPa")
    print(f"         Number of rebars = {len(point_geoms)}")
    print(f"         Area per rebar = {point_geoms[0].area:.1f} mm²")
    print(f"         Total reinf area = {len(point_geoms) * point_geoms[0].area:.0f} mm²")

    total_reinf_force = 0
    reinf_forces = []

    print(f"\n         Individual rebar forces:")
    for i, pg in enumerate(point_geoms[:5]):  # Show first 5
        z_s = pg.point.y
        y_s = pg.point.x

        # Bending strain at this location
        eps_bending = eps_0_inca + chi_y_inca * z_s

        # Total strain = prestress + bending
        eps_total = initial_strain + eps_bending

        # Get stress from constitutive law
        stress = pg.material.constitutive_law.get_stress(eps_total)

        # Force
        force = pg.area * stress
        total_reinf_force += force
        reinf_forces.append(force)

        print(f"         Rebar {i + 1}: z={z_s:+6.1f}mm, ε_bend={eps_bending * 1000:+.3f}‰, "
              f"ε_tot={eps_total * 1000:.3f}‰, σ={stress:+.0f}MPa, F={force / 1000:+.1f}kN")

    # Sum all rebars
    total_reinf_force = 0
    for pg in point_geoms:
        z_s = pg.point.y
        eps_bending = eps_0_inca + chi_y_inca * z_s
        eps_total = initial_strain + eps_bending
        stress = pg.material.constitutive_law.get_stress(eps_total)
        total_reinf_force += pg.area * stress

    print(f"\n         Total reinforcement force = {total_reinf_force / 1e6:+.4f} MN")
    print(f"         INCA2 reports σ_reinf = 2027-2058 MPa")

    # Expected from INCA2
    inca2_reinf_stress = 2040  # MPa average
    inca2_reinf_force = len(point_geoms) * point_geoms[0].area * inca2_reinf_stress
    print(f"         Expected from INCA2: {inca2_reinf_force / 1e6:.4f} MN")

    # --- Concrete contribution ---
    print(f"\n    [4b] CONCRETE (by difference)")
    concrete_force = N_total - total_reinf_force
    print(f"         Concrete force = N_total - F_reinf")
    print(f"                        = {N_total / 1e6:.4f} - {total_reinf_force / 1e6:.4f}")
    print(f"                        = {concrete_force / 1e6:+.4f} MN")

    # Expected concrete compression for equilibrium
    expected_concrete = -total_reinf_force
    print(f"\n         For N=0, need concrete = {expected_concrete / 1e6:+.4f} MN")
    print(f"         Deficit = {(expected_concrete - concrete_force) / 1e6:.4f} MN")

    # ================================================================
    # CHECK CONCRETE COMPRESSION ZONE
    # ================================================================
    print(f"\n[5] COMPRESSION ZONE ANALYSIS")

    # Get concrete geometry
    for geo in section.geometry.geometries:
        if hasattr(geo, 'polygon'):
            poly = geo.polygon
            total_area = poly.area
            print(f"    Total concrete area = {total_area:.0f} mm²")

            # Estimate compression zone area
            from shapely.geometry import box
            clip_box = box(-2000, z_neutral, 2000, zmax + 100)
            compression_zone = poly.intersection(clip_box)

            if not compression_zone.is_empty:
                comp_area = compression_zone.area
                print(f"    Compression zone area = {comp_area:.0f} mm²")

                # With fcd
                fcd = 0.85 * 50 / 1.5  # = 28.33 MPa
                max_comp_force = comp_area * fcd
                print(f"    fcd = {fcd:.2f} MPa")
                print(f"    Max compression (if full fcd) = {max_comp_force / 1e6:.4f} MN")

                # How much area would we need?
                needed_area = abs(expected_concrete) / fcd
                print(f"\n    Area needed for equilibrium = {needed_area:.0f} mm²")
                print(f"    Available area = {comp_area:.0f} mm²")
                print(f"    Ratio = {comp_area / needed_area:.2f}")

    # ================================================================
    # INCA2 vs PYTHON SUMMARY
    # ================================================================
    print(f"\n" + "=" * 80)
    print("SUMMARY: INCA2 vs PYTHON")
    print("=" * 80)
    print(f"{'Parameter':<35} {'Python':>15} {'INCA2':>15} {'Match':>10}")
    print("-" * 80)
    print(f"{'Curvature χ [1/mm]':<35} {chi_y_inca:>15.2e} {-23.6774e-6:>15.2e} {'✓':>10}")
    print(f"{'ε_top [‰]':<35} {eps_top_check * 1000:>15.3f} {-3.5:>15.3f} {'✓':>10}")
    print(f"{'ε_bot [‰]':<35} {eps_bot_check * 1000:>15.3f} {4.978:>15.3f} {'✓':>10}")
    print(f"{'Reinforcement force [MN]':<35} {total_reinf_force / 1e6:>+15.3f} {'+3.8 (est)':>15} {'~✓':>10}")
    print(f"{'Concrete force [MN]':<35} {concrete_force / 1e6:>+15.3f} {'-3.8 (est)':>15} {'❌':>10}")
    print(f"{'Total N [MN]':<35} {N_total / 1e6:>+15.3f} {'≈0':>15} {'❌':>10}")
    print(f"{'Moment |M| [kNm]':<35} {abs(My_total) / 1e6:>15.2f} {100.64:>15.2f} {'❌':>10}")
    print("=" * 80)

    print(f"""
CONCLUSION:
-----------
The reinforcement forces match reasonably well (~4 MN tension).
The concrete compression is severely underestimated in Python!

Python computes only {abs(concrete_force) / 1e6:.2f} MN compression,
but needs {abs(expected_concrete) / 1e6:.2f} MN for equilibrium.

Possible causes:
1. Concrete constitutive law not applying full fcd in compression zone
2. Integration not capturing the full compression zone area
3. Different concrete behavior in the stress integration

Next step: Check the concrete stress values directly at various points.
""")

    # ================================================================
    # CHECK CONCRETE STRESSES AT SPECIFIC POINTS
    # ================================================================
    print(f"\n[6] CONCRETE STRESS CHECK AT SPECIFIC POINTS")

    conc = None
    for geo in section.geometry.geometries:
        if hasattr(geo, 'material'):
            conc = geo.material
            break

    if conc:
        print(f"    Concrete constitutive law: {conc.constitutive_law}")
        print(f"    Checking stresses at key strains:")

        test_strains = [-0.0035, -0.003, -0.002, -0.001, 0.0, 0.001]
        for eps in test_strains:
            sig = conc.constitutive_law.get_stress(eps)
            print(f"      ε = {eps * 1000:+.2f}‰  →  σ = {sig:+.2f} MPa")

        print(f"\n    INCA2 shows σ_concrete max = -28.33 MPa at ε = -3.5‰")
        sig_at_crush = conc.constitutive_law.get_stress(-0.0035)
        print(f"    Python σ at ε=-3.5‰ = {sig_at_crush:.2f} MPa")

    return N_total, total_reinf_force, concrete_force


if __name__ == "__main__":
    detailed_inca2_comparison()