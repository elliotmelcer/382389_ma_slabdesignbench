"""
Debug script to track down the sign flip in m_cr calculation.

Run this with the problematic parameters from your penalized demo:
  - Hx_Hges: 0.2
  - height: 650
  - thickness: 85
  - etc.

This will trace through all intermediate values to find where the sign flips.
"""

from copy import deepcopy
import numpy as np
from matplotlib import pyplot as plt

from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic

from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm,
    sls_section,
    get_concrete,
)
from core.visualization_core.visualization import plot_cross_section
from slab_construction.slab_construction import FloorMaterial, FloorLayer, Floor, SlabConstruction
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab

set_design_code('ec2_2004')


def debug_cracking_moment(section, n: float = 0.0):
    """
    Enhanced version of calculate_cracking_moment_sls with full debugging output.
    """
    print("=" * 60)
    print("DEBUG: calculate_cracking_moment_sls")
    print("=" * 60)

    # Step 1: Create SLS section
    sls_sec = sls_section(section, concrete_tension=True)
    analysis_sls_sec = deepcopy(sls_sec)

    # Step 2: Get concrete properties
    conc = None
    for geo in analysis_sls_sec.geometry.geometries:
        if hasattr(geo, 'concrete') and geo.concrete:
            conc = geo.material
            break

    if conc is None:
        raise ValueError("No concrete geometry found in section")

    Ecm = conc.Ecm
    fctm = conc.fctm
    eps_ctm = fctm / Ecm

    print(f"\n[CONCRETE PROPERTIES]")
    print(f"  Ecm = {Ecm:.2f} MPa")
    print(f"  fctm = {fctm:.2f} MPa")
    print(f"  eps_ctm = {eps_ctm:.6f} (cracking strain, should be POSITIVE)")

    # Step 3: Get section extents
    _, _, zmin, zmax = analysis_sls_sec.geometry.calculate_extents()

    print(f"\n[SECTION GEOMETRY]")
    print(f"  zmin = {zmin:.2f} mm (bottom fiber)")
    print(f"  zmax = {zmax:.2f} mm (top fiber)")
    print(f"  depth = {zmax - zmin:.2f} mm")

    # Step 4: Get reinforcement positions
    point_geometries = analysis_sls_sec.geometry.point_geometries
    print(f"\n[REINFORCEMENT]")
    print(f"  Number of reinforcement points: {len(point_geometries)}")
    for i, pg in enumerate(point_geometries):
        z_s = pg.point.y
        eps_ini = pg.material.initial_strain if hasattr(pg.material, 'initial_strain') else 0.0
        print(f"  Rebar {i + 1}: z = {z_s:.2f} mm, eps_ini = {eps_ini:.6f}")

    # Step 5: Check centroid
    cz = analysis_sls_sec.gross_properties.cz
    print(f"\n[CENTROID]")
    print(f"  cz = {cz:.2f} mm")
    print(f"  Distance from bottom to centroid: {cz - zmin:.2f} mm")
    print(f"  Distance from centroid to top: {zmax - cz:.2f} mm")

    # Step 6: Run bisection with verbose output
    calculator = analysis_sls_sec.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    chi_min = -1e-3
    chi_max = 1e-3

    print(f"\n[BISECTION SETUP]")
    print(f"  Initial chi range: [{chi_min:.6f}, {chi_max:.6f}]")
    print(f"  Target: eps(zmin) = eps_ctm = {eps_ctm:.6f}")
    print(f"  Formula: eps_0 = eps_ctm - chi_y * zmin")

    # Test at bounds
    eps_0_a = eps_ctm - chi_min * zmin
    eps_0_b = eps_ctm - chi_max * zmin

    print(f"\n[BISECTION BOUNDS]")
    print(f"  At chi_min = {chi_min:.6f}:")
    print(f"    eps_0 = {eps_ctm:.6f} - ({chi_min:.6f}) * ({zmin:.2f}) = {eps_0_a:.6f}")
    print(f"  At chi_max = {chi_max:.6f}:")
    print(f"    eps_0 = {eps_ctm:.6f} - ({chi_max:.6f}) * ({zmin:.2f}) = {eps_0_b:.6f}")

    # Run actual bisection
    ITMAX = 100
    tolerance = 1e-2

    N_a, _, _, integration_data = calculator.integrator.integrate_strain_response_on_geometry(
        analysis_sls_sec.geometry,
        [eps_0_a, chi_min, 0.0],
        integration_data=integration_data,
        mesh_size=mesh_size
    )
    dn_a = N_a - n

    N_b, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
        analysis_sls_sec.geometry,
        [eps_0_b, chi_max, 0.0],
        integration_data=integration_data,
        mesh_size=mesh_size
    )
    dn_b = N_b - n

    print(f"\n[BISECTION INITIAL FORCES]")
    print(f"  At chi_min: N = {N_a:.2f} N, dN = {dn_a:.2f} N")
    print(f"  At chi_max: N = {N_b:.2f} N, dN = {dn_b:.2f} N")
    print(f"  Signs bracket zero? {dn_a * dn_b < 0}")

    # Bisection loop
    it = 0
    while abs(dn_a - dn_b) > tolerance and it < ITMAX:
        chi_c = (chi_min + chi_max) / 2.0
        eps_0_c = eps_ctm - chi_c * zmin

        N_c, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
            analysis_sls_sec.geometry,
            [eps_0_c, chi_c, 0.0],
            integration_data=integration_data,
            mesh_size=mesh_size
        )
        dn_c = N_c - n

        if dn_c * dn_a < 0:
            chi_max = chi_c
            dn_b = dn_c
        else:
            chi_min = chi_c
            dn_a = dn_c

        it += 1

    chi_y_eq = chi_c
    eps_0_eq = eps_0_c

    print(f"\n[BISECTION RESULT]")
    print(f"  Iterations: {it}")
    print(f"  chi_y = {chi_y_eq:.9f} 1/mm")
    print(f"  eps_0 = {eps_0_eq:.9f}")

    # Check strain at key points
    eps_bottom = eps_0_eq + chi_y_eq * zmin
    eps_top = eps_0_eq + chi_y_eq * zmax
    eps_centroid = eps_0_eq + chi_y_eq * cz

    print(f"\n[STRAIN PROFILE CHECK]")
    print(f"  eps(zmin) = {eps_0_eq:.6f} + {chi_y_eq:.9f} * {zmin:.2f} = {eps_bottom:.6f}")
    print(f"  eps(zmax) = {eps_0_eq:.6f} + {chi_y_eq:.9f} * {zmax:.2f} = {eps_top:.6f}")
    print(f"  eps(cz)   = {eps_0_eq:.6f} + {chi_y_eq:.9f} * {cz:.2f} = {eps_centroid:.6f}")
    print(f"  Expected eps(zmin) = eps_ctm = {eps_ctm:.6f}")
    print(f"  Match? {abs(eps_bottom - eps_ctm) < 1e-6}")

    # Final moment calculation
    strain_profile = [eps_0_eq, chi_y_eq, 0.0]
    N_cr, My_cr, Mz_cr = analysis_sls_sec.section_calculator.integrate_strain_profile(
        strain=strain_profile,
        integrate='stress'
    )

    print(f"\n[FINAL STRESS RESULTANTS]")
    print(f"  N_cr = {N_cr:.2f} N")
    print(f"  My_cr = {My_cr:.2f} Nmm = {My_cr / 1e6:.4f} kNm")
    print(f"  Mz_cr = {Mz_cr:.2f} Nmm")

    print(f"\n[SIGN ANALYSIS]")
    print(f"  My_cr is {'POSITIVE' if My_cr > 0 else 'NEGATIVE'}")
    print(f"  After negation in DeflectionLimitByMcrCheckEC2004DE:")
    print(f"    m_cr = -{My_cr / 1e6:.4f} = {-My_cr / 1e6:.4f} kNm")

    if My_cr > 0:
        print(f"\n  ⚠️  WARNING: My_cr is POSITIVE - this will result in NEGATIVE m_cr!")
        print(f"      This is the source of your bug.")
        print(f"\n  Possible causes:")
        print(f"    1. Section orientation is flipped (reinforcement at top instead of bottom)")
        print(f"    2. chi_y has wrong sign for this geometry")
        print(f"    3. The HP shell geometry creates an inverted section for these parameters")

    return {
        'section': sls_sec,
        'm_cr': My_cr,
        'strain_profile': strain_profile,
        'zmin': zmin,
        'zmax': zmax,
        'chi_y': chi_y_eq,
        'eps_0': eps_0_eq,
    }


def main():
    """
    Recreate the problematic slab construction from your penalized demo.
    """
    print("=" * 60)
    print("RECREATING PROBLEMATIC SLAB CONSTRUCTION")
    print("=" * 60)

    # Parameters from your debug output
    span_L = 7000.0
    width_B = 1520.0
    height = 650.0
    Hx_Hges = 0.2
    thickness = 85.0
    nt = 15
    dy = 190.0
    fck = 30.0
    prestress_pct = 0.4  # 40%
    reinf_area = 100.5

    # Calculate Hx and Hy
    Hx = Hx_Hges * height
    Hy = (1 - Hx_Hges) * height

    print(f"\n[GEOMETRY PARAMETERS]")
    print(f"  span_L = {span_L} mm")
    print(f"  width_B = {width_B} mm")
    print(f"  height = {height} mm (Hx + Hy)")
    print(f"  Hx = {Hx} mm")
    print(f"  Hy = {Hy} mm")
    print(f"  thickness = {thickness} mm")
    print(f"  nt = {nt}")
    print(f"  dy = {dy} mm")

    # Create materials
    concrete_uls = create_concrete(
        fck=fck,
        constitutive_law='parabolarectangle',
        alpha_cc=0.85,
        gamma_c=1.5,
        name=f"C{fck} ULS"
    )

    # CFRP reinforcement properties (Q142)
    fyk = 2200
    ftk = 2200
    Es = 220000
    epsuk = 10 / 1000  # 10 promille
    density = 1800

    brittle_elastic = Elastic(Es, eps_u=epsuk)
    initial_strain = prestress_pct * epsuk

    reinforcement = create_reinforcement(
        fyk=fyk,
        Es=Es,
        ftk=ftk,
        epsuk=epsuk,
        density=density,
        constitutive_law=brittle_elastic,
        initial_strain=initial_strain,
        gamma_s=1.3,
        name=f"Q142 prestressed {prestress_pct * 100}%"
    )

    print(f"\n[MATERIAL PARAMETERS]")
    print(f"  Concrete: C{fck}")
    print(f"  Reinforcement: Q142, prestress = {prestress_pct * 100}%")
    print(f"  initial_strain = {initial_strain:.6f}")

    # Create HP geometry
    hp_geom = HPGeometry(
        B=width_B,
        L=span_L,
        Hx=Hx,
        Hy=Hy,
        t=thickness,
        dy=dy,
        nt=nt
    )

    # Create HP shell
    hp_shell = HPShell(hp_geom, concrete_uls, reinforcement, reinf_area=reinf_area)

    # Get section at midspan
    section_midspan = hp_shell.section_at(0.5)

    print(f"\n[SECTION AT MIDSPAN]")

    # Plot the section first
    fig, ax = plt.subplots(figsize=(12, 8))
    plot_cross_section(section_midspan, ax=ax, x=0.5)
    ax.set_title("Section at midspan (x=0.5) - Check reinforcement position!")

    # Run the debug analysis
    result = debug_cracking_moment(section_midspan, n=0)

    # Additional check: what do the reinforcement z-coordinates look like?
    print(f"\n[REINFORCEMENT POSITION CHECK]")
    zmin = result['zmin']
    zmax = result['zmax']
    cz = section_midspan.gross_properties.cz

    for i, pg in enumerate(section_midspan.geometry.point_geometries):
        z_s = pg.point.y
        relative_pos = (z_s - zmin) / (zmax - zmin)
        print(f"  Rebar {i + 1}: z = {z_s:.2f} mm")
        print(f"    Relative position (0=bottom, 1=top): {relative_pos:.2f}")
        print(f"    Below centroid? {z_s < cz}")

    plt.tight_layout()
    plt.show()

    return result


if __name__ == "__main__":
    result = main()