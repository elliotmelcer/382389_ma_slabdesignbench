from copy import deepcopy
from dataclasses import asdict

import numpy as np
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.geometry import  CompoundGeometry, SurfaceGeometry
from structuralcodes.materials.concrete import Concrete, create_concrete
from structuralcodes.materials.reinforcement import Reinforcement
from structuralcodes.sections import GenericSection, GenericSectionCalculator

from core.analysis_core.material_methods import sargin_elastic_law, get_cube, sargin_elastic_cracking_law


#
# def calculate_cracking_moment_sls_Nmm(section: GenericSection, n: float = 0.0) -> dict:
#     """
#     Author: Elliot Melcer
#     Calculate cracking moment of a prestressed GenericSection.
#
#     The function finds the strain profile where the bottom fiber reaches
#     the cracking strain eps_ctm = fctm / Ecm, while maintaining equilibrium
#     with the applied axial force n.
#
#     Args:
#         section: GenericSection object (should be ULS section)
#         n: Applied axial force (positive = tension, negative = compression)
#
#     Returns:
#         dict: Dictionary containing:
#             - m_cr: Cracking moment (Nmm)
#             - strain_profile: [eps_0, chi_y, chi_z] at cracking
#             - reinforcement_strains: List of strains in each reinforcement
#             - stress_resultants: [N, My, Mz] at cracking
#     """
#
#     sls_sec = sls_section(section, concrete_tension=True)
#
#     analysis_sls_sec = deepcopy(sls_sec)
#
#     # --- Concrete Properties ---
#     # Find concrete geometry (assume first surface geometry with concrete)
#     conc = None
#     for geo in analysis_sls_sec.geometry.geometries:
#         if hasattr(geo, 'concrete') and geo.concrete:
#             conc = geo.material
#             break
#
#     if conc is None:
#         raise ValueError("No concrete geometry found in section")
#
#     # Get concrete properties
#     Ecm = conc.Ecm
#     fctm = conc.fctm
#     eps_ctm = fctm / Ecm  # Cracking strain
#
#     # Get section extents
#     _, _, zmin, zmax = analysis_sls_sec.geometry.calculate_extents()
#
#     # --- Get Reinforcement Properties ---
#     point_geometries = analysis_sls_sec.geometry.point_geometries
#     n_reinf = len(point_geometries)
#
#     if n_reinf == 0:
#         print("Warning: No reinforcement found in section")
#
#     # Extract reinforcement data
#     z_reinforcements = []
#     eps_ini_list = []
#     E_s_list = []
#     a_s_list = []
#
#     for pg in point_geometries:
#         z_reinforcements.append(pg.point.y)  # z-coordinate
#
#         # Initial strain (prestress)
#         eps_ini = pg.material.initial_strain if hasattr(pg.material, 'initial_strain') else 0.0
#         if eps_ini is None:
#             eps_ini = 0.0
#         eps_ini_list.append(eps_ini)
#
#         # Material properties
#         E_s = pg.material.Es if hasattr(pg.material, 'Es') else pg.material.constitutive_law.get_tangent(0)
#         E_s_list.append(E_s)
#
#         # Area
#         a_s_list.append(pg.area)
#
#     # --- Find Strain Profile at Cracking ---
#     # At cracking, the bottom fiber has strain eps_ctm
#     # Strain profile: eps(z) = eps_0 + chi_y * z + chi_z * y
#     # For uniaxial bending (about y-axis): chi_z = 0
#     # So: eps(z) = eps_0 + chi_y * z
#
#     # Bottom fiber: eps(zmin) = eps_ctm
#     # This gives: eps_ctm = eps_0 + chi_y * zmin
#
#     # We need to find eps_0 and chi_y such that:
#     # 1. eps(zmin) = eps_ctm (bottom fiber at cracking)
#     # 2. Internal axial force equals external force n
#
#     # From condition 1: eps_0 = eps_ctm - chi_y * zmin
#
#     # Use bisection to find curvature that gives equilibrium
#     # while keeping bottom fiber at cracking strain
#
#     calculator = analysis_sls_sec.section_calculator
#
#     # Get integration data if it exists, otherwise None
#     integration_data = getattr(calculator, 'integration_data', None)
#     mesh_size = getattr(calculator, 'mesh_size', 0.01)
#
#     # Define a reasonable range for curvature
#     # Start with very small curvature
#     chi_min = -1e-3
#     chi_max = 1e-3
#
#     ITMAX = 100
#     tolerance = 1e-2  # Force tolerance in N
#
#     try:
#         # Evaluate at bounds
#         eps_0_a = eps_ctm - chi_min * zmin
#         N_a, _, _, integration_data = calculator.integrator.integrate_strain_response_on_geometry(
#             analysis_sls_sec.geometry,
#             [eps_0_a, chi_min, 0.0],
#             integration_data=integration_data,
#             mesh_size=mesh_size
#         )
#         dn_a = N_a - n
#
#         eps_0_b = eps_ctm - chi_max * zmin
#         N_b, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
#             analysis_sls_sec.geometry,
#             [eps_0_b, chi_max, 0.0],
#             integration_data=integration_data,
#             mesh_size=mesh_size
#         )
#         dn_b = N_b - n
#
#         # Check if solution is within range of chi_min and chi_max
#         if dn_a * dn_b > 0:
#             # Expand the search range
#             print("Warning: Initial range doesn't bracket solution, expanding search...")
#             if abs(dn_a) < abs(dn_b):
#                 chi_max = chi_min
#                 chi_min = chi_min - 0.01
#             else:
#                 chi_min = chi_max
#                 chi_max = chi_max + 0.01
#
#             eps_0_a = eps_ctm - chi_min * zmin
#             N_a, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
#                 analysis_sls_sec.geometry,
#                 [eps_0_a, chi_min, 0.0],
#                 integration_data=integration_data,
#                 mesh_size=mesh_size
#             )
#             dn_a = N_a - n
#
#         # Bisection algorithm
#         it = 0
#         while abs(dn_a - dn_b) > tolerance and it < ITMAX:
#             chi_c = (chi_min + chi_max) / 2.0
#             eps_0_c = eps_ctm - chi_c * zmin
#
#             N_c, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
#                 analysis_sls_sec.geometry,
#                 [eps_0_c, chi_c, 0.0],
#                 integration_data=integration_data,
#                 mesh_size=mesh_size
#             )
#             dn_c = N_c - n
#
#             if dn_c * dn_a < 0:
#                 chi_max = chi_c
#                 dn_b = dn_c
#             else:
#                 chi_min = chi_c
#                 dn_a = dn_c
#
#             it += 1
#
#         if it >= ITMAX:
#             print(f"Warning: Maximum iterations reached. Force imbalance: {dn_c:.2f} N")
#
#         # Use final values
#         chi_y_eq = chi_c
#         eps_0_eq = eps_0_c
#         strain_profile = [eps_0_eq, chi_y_eq, 0.0]
#
#         # --- Calculate Reinforcement Strains ---
#         reinforcement_strains = []
#         for i, z_s in enumerate(z_reinforcements):
#             # Total strain = initial strain + bending strain
#             eps_bending = eps_0_eq + chi_y_eq * z_s
#             eps_total = eps_ini_list[i] + eps_bending
#             reinforcement_strains.append(eps_total)
#
#         # --- Calculate Internal Forces ---
#         N_cr, My_cr, Mz_cr = analysis_sls_sec.section_calculator.integrate_strain_profile(
#             strain=strain_profile,
#             integrate='stress'
#         )
#
#         # Return results_c1_1
#         return {
#             'section': sls_sec,
#             'm_cr': My_cr,
#             'strain_profile': strain_profile,
#         }
#
#     except Exception as e:
#         print(f"Error in equilibrium calculation: {e}")
#         raise

def calculate_cracking_moment_sls_Nmm(section, n: float = 0.0):
    """
    Calculate the cracking moment for a section at SLS.

    The function finds the strain profile where the bottom fiber reaches
    the cracking strain eps_ctm = fctm / Ecm, while maintaining equilibrium
    with the applied axial force n.

    IMPORTANT: This version includes physical strain limit checks to prevent
    finding spurious solutions where concrete would crush before cracking.

    Args:
        section: GenericSection object (should be ULS section)
        n: Applied axial force (positive = tension, negative = compression)

    Returns:
        dict: Dictionary containing:
            - m_cr: Cracking moment (Nmm), or float('-inf') if section crushes before cracking
            - strain_profile: [eps_0, chi_y, chi_z] at cracking
            - valid: True if physically valid solution found
            - reason: Explanation if invalid
    """

    sls_sec = sls_section(section, concrete_tension=True)
    analysis_sls_sec = deepcopy(sls_sec)

    # --- Concrete Properties ---
    conc = None
    for geo in analysis_sls_sec.geometry.geometries:
        if hasattr(geo, 'concrete') and geo.concrete:
            conc = geo.material
            break

    if conc is None:
        raise ValueError("No concrete geometry found in section")

    Ecm = conc.Ecm
    fctm = conc.fctm
    eps_ctm = fctm / Ecm  # Cracking strain (positive, tension)

    # Get ultimate compressive strain (negative)
    eps_cu1 = -abs(conc.eps_cu1) if hasattr(conc, 'eps_cu1') else -0.0035

    # --- Section Geometry ---
    _, _, zmin, zmax = analysis_sls_sec.geometry.calculate_extents()
    section_depth = zmax - zmin

    # --- Reinforcement Properties ---
    point_geometries = analysis_sls_sec.geometry.point_geometries

    z_reinforcements = []
    eps_ini_list = []

    for pg in point_geometries:
        z_reinforcements.append(pg.point.y)
        eps_ini = pg.material.initial_strain if hasattr(pg.material, 'initial_strain') else 0.0
        if eps_ini is None:
            eps_ini = 0.0
        eps_ini_list.append(eps_ini)

    # ============================================================
    # CALCULATE PHYSICAL LIMITS ON CURVATURE
    # ============================================================
    #
    # Strain profile: eps(z) = eps_0 + chi_y * z
    # Cracking condition: eps(zmin) = eps_ctm
    #   => eps_0 = eps_ctm - chi_y * zmin
    #
    # Top fiber strain: eps_top = eps_0 + chi_y * zmax
    #                           = eps_ctm + chi_y * (zmax - zmin)
    #
    # Physical constraint: eps_top >= eps_cu1 (no crushing)
    #   => chi_y >= (eps_cu1 - eps_ctm) / (zmax - zmin)
    #
    # Note: For sagging bending, chi_y is negative, so this is a LOWER BOUND

    chi_min_physical = (eps_cu1 - eps_ctm) / section_depth

    # ============================================================
    # SET UP BISECTION WITH PHYSICAL CONSTRAINTS
    # ============================================================

    calculator = analysis_sls_sec.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    # Initial search range - constrained by physical limit
    chi_min = chi_min_physical * 1.001  # Just inside the valid range (less negative)
    chi_max = 1e-3  # Small positive curvature (hogging)

    ITMAX = 100
    tolerance = 1e-2  # Force tolerance in N

    try:
        # Evaluate at bounds
        eps_0_a = eps_ctm - chi_min * zmin
        N_a, _, _, integration_data = calculator.integrator.integrate_strain_response_on_geometry(
            analysis_sls_sec.geometry,
            [eps_0_a, chi_min, 0.0],
            integration_data=integration_data,
            mesh_size=mesh_size
        )
        dn_a = N_a - n

        eps_0_b = eps_ctm - chi_max * zmin
        N_b, _, _, _ = calculator.integrator.integrate_strain_response_on_geometry(
            analysis_sls_sec.geometry,
            [eps_0_b, chi_max, 0.0],
            integration_data=integration_data,
            mesh_size=mesh_size
        )
        dn_b = N_b - n

        # Check if solution exists within valid range
        if dn_a * dn_b > 0:
            # No zero crossing in valid range
            # This means the section cannot crack without crushing first

            # Determine which side we're on
            if dn_a > 0 and dn_b > 0:
                reason = "Prestress too high - section would crush before cracking (N > 0 throughout valid range)"
            else:
                reason = "No equilibrium solution in valid curvature range"

            return {
                'section': sls_sec,
                'm_cr': float('-inf'),
                'strain_profile': [0.0, chi_min_physical, 0.0],
                'valid': False,
                'reason': reason,
                'chi_min_physical': chi_min_physical,
            }

        # Bisection algorithm (within valid range)
        chi_c = chi_min
        dn_c = dn_a

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

        if it >= ITMAX:
            print(f"Warning: Maximum iterations reached. Force imbalance: {dn_c:.2f} N")

        # Final solution
        chi_y_eq = chi_c
        eps_0_eq = eps_ctm - chi_y_eq * zmin
        strain_profile = [eps_0_eq, chi_y_eq, 0.0]

        # Verify solution is within physical limits (should be, but double-check)
        eps_top = eps_0_eq + chi_y_eq * zmax
        if eps_top < eps_cu1:
            return {
                'section': sls_sec,
                'm_cr': float('-inf'),
                'strain_profile': strain_profile,
                'valid': False,
                'reason': f"Solution exceeds concrete crushing strain (eps_top={eps_top:.4f} < eps_cu1={eps_cu1:.4f})",
            }

        # --- Calculate Internal Forces ---
        N_cr, My_cr, Mz_cr = analysis_sls_sec.section_calculator.integrate_strain_profile(
            strain=strain_profile,
            integrate='stress'
        )

        return {
            'section': sls_sec,
            'm_cr': My_cr,
            'strain_profile': strain_profile,
            'valid': True,
            'reason': None,
            'eps_top': eps_top,
        }

    except Exception as e:
        print(f"Error in equilibrium calculation: {e}")
        raise

def calculate_bending_strength_sls_Nmm(section: GenericSection, n: float = 0.0) -> dict:
    """
    Author: Elliot Melcer
    Returns a triplet of:
        SLS Section
        SLS Bending Strength in Nmm
        Associated Strain Profile
    """

    sls_sec = sls_section(section, concrete_tension=False)

    analysis_sls_sec = deepcopy(sls_sec) # in reference to structuralcodes issue #303 https://github.com/fib-international/structuralcodes/issues/303

    bending_strength_result = analysis_sls_sec.section_calculator.calculate_bending_strength(n = n)

    m_u = bending_strength_result.m_y

    chi_y = bending_strength_result.chi_y
    eps_0 = bending_strength_result.eps_a
    strain_profile = [eps_0, chi_y, 0.0]

    return {
        'section': sls_sec,
        'm_u': m_u,
        'strain_profile': strain_profile,
    }

def calculate_bending_strength_uls_Nmm(section: GenericSection, n: float = 0.0) -> dict:
    """
    Author: Elliot Melcer
    Returns a triplet of:
        ULS Section
        ULS Bending Strength in Nmm
        Associated Strain Profile
    """

    analysis_section = deepcopy(section) # in reference to structuralcodes issue #303 https://github.com/fib-international/structuralcodes/issues/303

    bending_strength_result = analysis_section.section_calculator.calculate_bending_strength(n=n)

    m_u = bending_strength_result.m_y

    chi_y = bending_strength_result.chi_y
    eps_0 = bending_strength_result.eps_a
    strain_profile = [eps_0, chi_y, 0.0]

    return {
        'section': section,
        'm_u': m_u,
        'strain_profile': strain_profile,
    }

def calculate_moment_curvature_sls(section: GenericSection,
                                   n: float = 0.0,
                                   include_prestress_branch: bool = True,
                                   concrete_tension: bool = False,
                                   cracking: bool = True,
                                   debug: bool = False) -> MomentCurvatureResults:
    """
    Author: Elliot Melcer
    Returns the Results of a Moment-Curvature calculation for the given section.

    For prestressed sections, adds initial state point (κ₀, M=0).

    :param cracking:
    :param section: GenericSection (ULS)
    :param n: Axial force [N]
    :param include_prestress_branch: If True, adds prestressed initial state
    :param concrete_tension: If False, fctm = 0
    :param debug:
    :return: MomentCurvatureResults with complete M-κ curve
    """
    sls_sec = sls_section(section, concrete_tension=concrete_tension, cracking = cracking)

    # --- Check which material governs failure ---
    # Get concrete ε_c1
    conc = None
    for geo in sls_sec.geometry.geometries:
        if hasattr(geo, 'concrete') and geo.concrete:
            conc = geo.material
            break
    eps_c1 = abs(conc.eps_c1)  # ~2.0–2.5‰ for typical concretes

    # Get bending strength strain profile
    m_u_res = calculate_bending_strength_sls_Nmm(section, n=n)
    eps_0, chi_y, _ = m_u_res["strain_profile"]
    _, _, zmin, zmax = sls_sec.geometry.calculate_extents()
    eps_top = eps_0 + chi_y * zmax  # concrete top fiber strain at failure

    # If concrete top exceeds ε_c1 at failure → concrete is in post-yield zone
    concrete_governs = abs(eps_top) > eps_c1
    num_post_yield = 10 if concrete_governs else 0

    # Get standard M-κ curve from library
    results = sls_sec.section_calculator.calculate_moment_curvature(
        n=n,
        num_pre_yield=40,
        num_post_yield=num_post_yield    # in case concrete is governing, at least 1 post yield point is necessary
    )

    # FIX SIGNS - Library may return negative values
    results.m_y = -np.abs(results.m_y)  # Make consistently negative
    results.chi_y = -np.abs(results.chi_y)  # Make consistently negative

    # Check if section is prestressed and we should add initial state
    if not include_prestress_branch:
        return results

    # Check for prestressed reinforcement
    has_prestress = False
    for pg in sls_sec.geometry.point_geometries:
        if hasattr(pg.material, 'initial_strain') and pg.material.initial_strain != 0:
            has_prestress = True
            break

    if not has_prestress:
        return results  # Not prestressed, return as-is

    # ============================================================
    # PRESTRESSED SECTION - ADD INITIAL STATE POINT (κ₀, M=0)
    # ============================================================

    # Calculate prestressing moment
    M_p = calculate_prestress_moment_Nmm(section)

    # Get cracking properties (using same material model)
    M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=n)

    # Determine initial curvature from prestressing kappa_0
    if M_cr_result.get('valid', True):
        # Method 1: Use M_cr and kappa_cr
        M_cr = abs(M_cr_result["m_cr"])  # Nmm
        kappa_cr = abs(M_cr_result["strain_profile"][1])  # 1/mm

        if abs(M_cr - M_p) > 1e-3:
            kappa_0 = (M_p * kappa_cr) / (M_cr - M_p)
        else:
            kappa_0 = 0.0
    else:
        # Method 2 fallback: Use initial slope of M-κ curve
        if len(results.chi_y) >= 5:
            slope, intercept = np.polyfit(results.chi_y[:2], results.m_y[:2], 1)

            kappa_0 = -intercept / slope if slope > 1e-6 else 0.0
        else:
            kappa_0 = 0.0

    # Add single initial state point at beginning
    moments_combined = np.concatenate([[0.0], results.m_y])
    curvatures_combined = np.concatenate([[kappa_0], results.chi_y])

    # Update results object
    results.m_y = moments_combined
    results.chi_y = curvatures_combined

    # Update other arrays to match length (if they exist)
    if hasattr(results, 'eps_axial') and results.eps_axial is not None:
        results.eps_axial = np.concatenate([[0.0], results.eps_axial])

    if debug:
        print(f"\n[DEBUG] Prestressed M-κ curve:")
        print(f"  Added initial state: (κ={kappa_0:.9f} 1/mm, M=0)")
        print(f"  Library starts at: (κ={results.chi_y[1]:.9f} 1/mm, M={results.m_y[1] / 1e6:.3f} kNm)")
        print(f"  Total points: {len(moments_combined)}")

    return results


def calculate_prestress_moment_Nmm(section) -> float:
    """
    Calculate the moment from prestressing forces.

    For each prestressed reinforcement:
    - F_p = A_s × ε_ini × E_s (prestressing force)
    - M_p = Σ(F_p × z_s) (moment from prestressing forces about centroid)

    :param section: SLS section with prestressed reinforcement
    :return: Prestressing moment [Nmm]
    """
    # Get section centroid
    cz = section.gross_properties.cz

    # Initialize moment
    M_p = 0.0

    # Get prestressed reinforcement point geometries
    if hasattr(section.geometry, 'point_geometries'):
        for pg in section.geometry.point_geometries:
            # Get reinforcement material
            reinf = pg.material

            # Check if reinforcement is prestressed
            if hasattr(reinf, 'initial_strain') and reinf.initial_strain is not None:
                eps_ini = reinf.initial_strain  # Initial strain from prestress

                # Skip if no prestress
                if abs(eps_ini) < 1e-10:
                    continue

                # Reinforcement properties
                E_s = reinf.Es  # MPa
                A_s = pg.area  # mm²
                z_s = pg.point.y  # z-coordinate (mm)

                # Prestressing force: F_p = A_s × eps_ini × E_s
                F_p = A_s * eps_ini * E_s  # N

                # Moment arm from centroid
                d = z_s - cz  # mm

                # Add contribution to total prestressing moment
                M_p += F_p * d

    return abs(M_p)

def get_strain_at_point(strain_profile, y, z) -> float:
    """
    Author: Elliot Melcer
    Calculate strain at point (y, z) given strain profile.

    Args:
        strain_profile: [eps_0, chi_y, chi_z]
        y: y-coordinate
        z: z-coordinate

    Returns:
        float: Strain at point (y, z)
    """
    eps_0, chi_y, chi_z = strain_profile
    return eps_0 + chi_y * z + chi_z * y

def sls_section(section_uls: GenericSection, concrete_tension: bool, cracking: bool = False) -> GenericSection:
    """
    Author: Elliot Melcer
    Returns the section with sls constitutive law for concrete
    """
    # get the geometry of the section
    geo = section_uls.geometry

    #create sls concrete from concrete used in section
    conc = get_concrete(section_uls)
    f_ck = conc.fck
    f_cube = get_cube(f_ck)

    # If Concrete should be able to take tension forces, use custom constitutive law (linear in tension and non-linear in compression)
    if concrete_tension:
        if cracking:
            concrete_sls = create_concrete(fck=f_ck, constitutive_law=sargin_elastic_cracking_law(conc), name = f"C{f_ck}/{f_cube} SLS")
        else:
            concrete_sls = create_concrete(fck=f_ck, constitutive_law=sargin_elastic_law(conc), name = f"C{f_ck}/{f_cube} SLS")
    # If Concrete should not be able to take tension forces, use sargin (nonlinear) constitutive law
    else:
        concrete_sls = create_concrete(fck=f_ck, constitutive_law='sargin', name=f"C{f_ck}/{f_cube} SLS")

    processed_geoms = []
    for g in geo.geometries:
        processed_geoms.append(
            SurfaceGeometry.from_geometry(geo=g, new_material=concrete_sls) # change concrete material
        )
    for pg in geo.point_geometries:
        processed_geoms.append(pg) # keep same reinforcement material

    new_sls_section = GenericSection(CompoundGeometry(geometries=processed_geoms), name = section_uls.name)

    return new_sls_section

def flipped_section(section: GenericSection) -> GenericSection:
    """
    Author: Elliot Melcer
    Returns the flipped section, to be used when calculating the bending strength at a support
    :param section:
    :return:
    """
    geometry = section.geometry

    gross_props = section.gross_properties

    centroid = (gross_props.cy, gross_props.cz)

    flipped_support_section_geometry = geometry.rotate(
        angle=180,
        point=centroid,
        use_radians=False)

    rotated_section = GenericSection(flipped_support_section_geometry, name = f"{section.name} (Support)")

    return rotated_section

def get_concrete(section: GenericSection) -> Concrete:
    """
    Author: Elliot Melcer
    Return the first concrete material found in the section geometry.
    Raises:
        ValueError: If no concrete material exists in the geometry.
    """
    # For CompoundGeometry, get material from the first surface geometry
    geometry = section.geometry
    if hasattr(geometry, 'geometries'):
        # CompoundGeometry - get concrete from first surface
        concrete = geometry.geometries[0].material
    else:
        # Simple SurfaceGeometry
        concrete = geometry.material

    return concrete

def get_reinforcement(section: GenericSection) -> tuple[Reinforcement, float]:
    """
    Author: Elliot Melcer
    Returns the first Reinforcement material found in the section geometry and the corresponding Reinforcement area
    (assumption: all Reinforcement diameters are the same).

    Raises:
        ValueError: If no reinforcement material is found.
    """

    geometry = section.geometry

    # simple surface / not compound? then nothing to check
    if not hasattr(geometry, "geometries"):
        raise ValueError("Geometry does not contain reinforcement points.")

    # compound → scan point geometries
    if hasattr(geometry, "point_geometries"):
        for geo in geometry.point_geometries:
            mat = getattr(geo, "material", None)
            area = (geo.diameter ** 2 / 4) * np.pi
            if isinstance(mat, Reinforcement):
                return mat, area

    raise ValueError("No reinforcement material found in section geometry.")

def get_number_of_reinforcements(section: GenericSection) -> int:
    """
    Author: Elliot Melcer
    Count the number of reinforcement point geometries in the section geometry.
    """
    geom = section.geometry
    n = len(geom.point_geometries)
    return n