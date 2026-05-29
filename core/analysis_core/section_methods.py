from copy import deepcopy

import numpy as np
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.geometry import  CompoundGeometry, SurfaceGeometry
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.reinforcement import Reinforcement
from structuralcodes.sections import GenericSection

from core.analysis_core.material_methods import create_sls_concrete_EC, TensionStiffeningConcreteLawEC, create_uls_concrete_EC

class InvalidSectionForMKError(ValueError):
    """Raised when a section cannot produce a valid M-K diagram
    (e.g., prestress too high → would crush before cracking)."""
    pass

def calculate_cracking_moment_sls_Nmm_EC(section, n: float = 0.0):
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

    sls_sec = sls_section_EC(section, "FCTM_PARABOLIC")
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
            reason = f"Solution exceeds concrete crushing strain (eps_top={eps_top:.4f} < eps_cu1={eps_cu1:.4f})"
            return {
                'section': sls_sec,
                'm_cr': float('-inf'),
                'strain_profile': strain_profile,
                'valid': False,
                'reason': reason,
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

def calculate_bending_strength_sls_Nmm_EC(section: GenericSection, n: float = 0.0) -> dict:
    """
    Author: Elliot Melcer
    Returns a triplet of:
        SLS Section
        SLS Bending Strength in Nmm
        Associated Strain Profile
    """

    sls_sec = sls_section_EC(section, "NONE_PARABOLIC")

    analysis_sls_sec = deepcopy(sls_sec) # in reference to structuralcodes issue #303 https://github.com/fib-international/structuralcodes/issues/303

    try:
        bending_strength_result = analysis_sls_sec.section_calculator.calculate_bending_strength(n=n)
    except ValueError as e:
        if "cannot be taken by section" in str(e):
            return {
                'section': analysis_sls_sec,
                'm_u': None,
                'strain_profile': None,
                'valid': False,
                'reason': str(e),
            }
        raise  # any other ValueError is a real bug, let it surface

    m_u = bending_strength_result.m_y

    chi_y = bending_strength_result.chi_y
    eps_0 = bending_strength_result.eps_a
    strain_profile = [eps_0, chi_y, 0.0]

    return {
        'section': sls_sec,
        'm_u': m_u,
        'strain_profile': strain_profile,
        'valid': True,
        'reason': None,
    }

def calculate_bending_strength_uls_Nmm_EC(section: GenericSection, n: float = 0.0) -> dict:
    """
    Author: Elliot Melcer
    Returns a triplet of:
        ULS Section
        ULS Bending Strength in Nmm
        Associated Strain Profile
    """

    # Safety Conversion to ULS Section in case SLS Section was passed
    analysis_section = uls_section_EC(section)

    try:
        bending_strength_result = analysis_section.section_calculator.calculate_bending_strength(n=n)
    except ValueError as e:
        if "cannot be taken by section" in str(e):
            return {
                'section': analysis_section,
                'm_u': None,
                'strain_profile': None,
                'valid': False,
                'reason': str(e),
            }
        raise  # any other ValueError is a real bug, let it surface

    m_u = bending_strength_result.m_y

    chi_y = bending_strength_result.chi_y
    eps_0 = bending_strength_result.eps_a
    strain_profile = [eps_0, chi_y, 0.0]

    return {
        'section': analysis_section,
        'm_u': m_u,
        'strain_profile': strain_profile,
        'valid': True,
        'reason': None,
    }


def calculate_moment_curvature_sls_EC(section: GenericSection,
                                      n: float = 0.0,
                                      constitutive_law: str = "TENSTIFF_PARABOLIC",
                                      simplification: bool | int | float = False,
                                      debug: bool = False) -> MomentCurvatureResults:
    """
    Author: Elliot Melcer
    Returns the Results of a Moment-Curvature calculation for the given section.

    For prestressed sections, adds initial state point (κ₀, M=0).

    :param section:             GenericSection (ULS)
    :param n:                   Axial force [N]
    :param simplification:  Control simplified M-K-Diagram Calculation in _simplified_moment_curvature_method()
    :param constitutive_law
    :param debug:

    :return: MomentCurvatureResults with complete M-κ curve
    """
    sls_sec = sls_section_EC(section, constitutive_law)

    if simplification is False:
        # Full M-K-Diagram
        results = _full_moment_curvature_method(
            section=sls_sec,
            n=n,
            debug=debug,
        )
    elif simplification is True or (isinstance(simplification, (int, float)) and simplification > 0):
        # Simplified M-K-Diagram
        results = _simplified_moment_curvature_method(
            section=sls_sec,
            simplification=simplification,
            n=n,
            debug=debug,
        )
    else:
        raise ValueError(f"simplification must be False, True, or a positive number, got {simplification!r}")

    mon_incr_results = _ensure_force_controlled(results)
    return mon_incr_results


def _ensure_force_controlled(results: MomentCurvatureResults) -> MomentCurvatureResults:
    """
    Author: Elliot Melcer
    Ensures the moment-curvature-diagram is force controlled by
    enforcing monotonically increasing moment magnitudes

    When |m[i+1]| < |m[i]|, collects all dip indices until the first j where
    |m[j]| > |m[i]|, inserts an interpolated point (κ_new, m[i]) at i+1, and
    removes the dip indices. If the moment never recovers, the tail is truncated.

    :param results: MomentCurvatureResults object (modified in-place).
    :return:        The same MomentCurvatureResults object with corrected arrays.
    """

    # Work with a single list of (moment, curvature) pairs so the two arrays
    # can never be modified independently and get out of sync.
    pairs = list(zip(results.m_y, results.chi_y))

    i = 0
    while i < len(pairs) - 1:

        if abs(pairs[i + 1][0]) < abs(pairs[i][0]):
            # ----------------------------------------------------------------
            # Dip detected: advance j until the moment recovers past m[i].
            # ----------------------------------------------------------------
            j = i + 1
            while j < len(pairs) and abs(pairs[j][0]) <= abs(pairs[i][0]):
                j += 1

            m_peak = pairs[i][0]  # signed peak moment (negative)

            if j < len(pairs):
                # ------------------------------------------------------------
                # Indices i+1 … j-2: set moment to m_peak, curvature unchanged.
                # ------------------------------------------------------------
                for k in range(i + 1, j - 1):
                    pairs[k] = (m_peak, pairs[k][1])

                # ------------------------------------------------------------
                # Index j-1: set moment to m_peak, interpolate curvature
                # between the original values at j-1 and j at M = m_peak.
                # ------------------------------------------------------------
                m_before = pairs[j - 1][0]
                m_after = pairs[j][0]
                chi_before = pairs[j - 1][1]
                chi_after = pairs[j][1]

                t = (m_peak - m_before) / (m_after - m_before)
                pairs[j - 1] = (m_peak, chi_before + t * (chi_after - chi_before))

            else:
                # ------------------------------------------------------------
                # Moment never recovers: set all remaining to m_peak,
                # curvatures unchanged.
                # ------------------------------------------------------------
                for k in range(i + 1, len(pairs)):
                    pairs[k] = (m_peak, pairs[k][1])

        i += 1

    # Unzip pairs and write corrected arrays back to the results object
    moments, curvatures = zip(*pairs) if pairs else ([], [])
    results.m_y = np.array(moments)
    results.chi_y = np.array(curvatures)

    return results


def _full_moment_curvature_method(section: GenericSection,
                                   n: float = 0.0,
                                   debug: bool = False) -> MomentCurvatureResults:
    """
    Author: Elliot Melcer
    Calculates the full moment-curvature-diagram for a given section and normal force.
    Moments are calculated for a list of curvatures that includes the cracking curvature
    using the calculate_moment_curvature()-method in StructuralCodes. If the section is
    prestressed, the prestress curvature point is added.
    
    :param section: section to be analyzed
    :param n:       normal force in N
    :param debug:   optional debugging flag
    :return:        MomentCurvatureResults-object
    """
    # ------------------------------------
    # Build custom curvature list to be evaluated for moment-curvature-diagram
    # Must include exactly the point of cracking to accurately reflect correct
    # cracking behavior
    # ------------------------------------

    # Get bending strength strain profile
    m_u_res = calculate_bending_strength_sls_Nmm_EC(section, n=n)
    eps_0, chi_u, _ = m_u_res["strain_profile"]

    # Get curvature at cracking
    M_cr_result = calculate_cracking_moment_sls_Nmm_EC(section)
    if not M_cr_result.get("valid", True):
        raise InvalidSectionForMKError(
            f"Cannot build full M-K diagram: cracking moment invalid "
            f"({M_cr_result.get('reason', 'unknown')})"
        )
    M_cr = M_cr_result["m_cr"]
    sp = section.section_calculator.calculate_strain_profile(0, M_cr, 0)
    _, kappa_cr, _ = sp

    # Standard-chi-Array + κ_cr deterministisch einfügen
    chi_default = np.linspace(-1e-8, chi_u, 40)
    chi_with_crack = np.sort(np.concatenate([chi_default, [kappa_cr]]))[::-1]  # für negative Krümmungen umkehren

    # -----------------------------------
    # Get standard M-κ curve from library
    #------------------------------------
    results = section.section_calculator.calculate_moment_curvature(
        n=n,
        chi = chi_with_crack
    )

    # FIX SIGNS - Library may return negative values
    results.m_y = -np.abs(results.m_y)  # Make consistently negative
    results.chi_y = -np.abs(results.chi_y)  # Make consistently negative

    # Check for prestressed reinforcement
    has_prestress = False
    for pg in section.geometry.point_geometries:
        if hasattr(pg.material, 'initial_strain') and pg.material.initial_strain != 0:
            has_prestress = True
            break

    if not has_prestress:
        return results  # Not prestressed, return as-is

    # -------------------------------------------------------
    # Calculate initial state point (κ₀, M=0)
    # -------------------------------------------------------

    kappa_0 = _calculate_kappa_0(section, n=n, mk_results=results, debug=debug)

    # -------------------------------------------------------
    # Stitch together moments and curvatures
    # -------------------------------------------------------

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

def _simplified_moment_curvature_method(section: GenericSection,
                                        simplification = None,
                                        n: float = 0.0,
                                        debug: bool = False) -> MomentCurvatureResults:
    """
    Author: Elliot Melcer
    Calculates a simplified trilinear version of calculate_moment_curvature_sls().
    Points:
        Prestress Point:        kappa_0 = - M_int * K_cr / (M_cr - M_int)
        Cracking Point
        End of Cracking Point:  based on tension stiffening of concrete Ultimate Point
    :param simplification: Optional simplification behavior:
                           Input   Range      Explanation
                           ------------------------------------------------------------------------------------------------
                           False              Do not use this simplified method (handled higher up, should not reach this code)
                           True               Use simplified method without extra points
                           int     n>=1       Creates n evenly distributed points between kappa_cr and kappa_eoc
                           float   0<n<1      Creates ONE additional point at kappa_cr + n * (kappa_eoc - kappa_cr)

    :param section:         section to be analyzed
    :param n:               normal force in N
    :param debug:           optional debugging flag
    :return:                MomentCurvatureResults-object
    """

    # Concrete Properties
    concrete_sls = get_concrete(section)
    law = concrete_sls.constitutive_law
    eps_F_t = law.eps_F_t

    # Check Constitutive Law
    if not isinstance(law, TensionStiffeningConcreteLawEC):
        raise Exception("Simplified M-K-Line only implemented for TENSTIFF_PARABOLIC")

    # Cracking Point
    M_cr_result = calculate_cracking_moment_sls_Nmm_EC(section, n=n)

    if not M_cr_result.get("valid", True):
        raise InvalidSectionForMKError(
            f"Cannot build simplified M-K diagram: cracking moment invalid "
            f"({M_cr_result.get('reason', 'unknown')})"
        )

    M_cr_Nmm = M_cr_result["m_cr"]  # Nmm
    kappa_cr = M_cr_result["strain_profile"][1]  # 1/mm

    # Prestress Point
    kappa_0 = _calculate_kappa_0(section, n=n, m_cr_result=M_cr_result, debug=debug)

    # End of Cracking Point
    eoc_results = _calculate_section_state_from_bottom_strain_sls(section_uls = section, n = n, eps_bot=eps_F_t, constitutive_law="TENSTIFF_PARABOLIC")
    _, kappa_eoc, _ = eoc_results["strain_profile"]

    Mk_res_eoc = section.section_calculator.calculate_moment_curvature(n = n, chi=[kappa_eoc])
    M_eoc_Nmm = Mk_res_eoc.m_y[0]

    # Ultimate Point
    ultimate_result = calculate_bending_strength_sls_Nmm_EC(section)
    M_u_Nmm = ultimate_result["m_u"]
    _, kappa_u, _ = ultimate_result["strain_profile"]

    # Extra Points
    kappa_extra = np.array([])

    if simplification is False:
        raise ValueError(
            "simplification=False means this simplified method should not be called. "
            "Handle this case higher up in the call chain."
        )

    elif simplification is True:
        # use simplified method, but without extra points
        pass

    elif type(simplification) is int:
        if simplification < 1:
            raise ValueError("If simplification is an int, it must be >= 1.")
        kappa_extra = np.linspace(kappa_cr, kappa_eoc, simplification + 2)[1:-1]

    elif type(simplification) is float:
        if not (0.0 < simplification < 1.0):
            raise ValueError("If simplification is a float, it must satisfy 0 < simplification < 1.")
        kappa_extra = np.array([kappa_cr + simplification * (kappa_eoc - kappa_cr)])

    else:
        raise TypeError(
            "simplification must be one of: False, True, int >= 1, or float with 0 < value < 1 "
            f"(got {type(simplification).__name__})"
        )

    # Compute Extra Moments
    if kappa_extra.size > 0:
        Mk_res_extra = section.section_calculator.calculate_moment_curvature(
            n=n, chi=kappa_extra
        )
        M_extra_Nmm = Mk_res_extra.m_y
    else:
        M_extra_Nmm = []

    # Assemble Simplified M-K-Pairs
    moments_pre_crack    = np.array([0.0,     M_cr_Nmm])
    curvatures_pre_crack = np.array([kappa_0, kappa_cr])

    moments_post_crack    = np.array([M_eoc_Nmm, M_u_Nmm])
    curvatures_post_crack = np.array([kappa_eoc, kappa_u])

    moments     = np.concatenate((moments_pre_crack,     M_extra_Nmm,    moments_post_crack))
    curvatures  = np.concatenate((curvatures_pre_crack,  kappa_extra,    curvatures_post_crack))

    mk_results = section.section_calculator.calculate_moment_curvature(n = n, chi=[])
    mk_results.m_y=moments
    mk_results.chi_y=curvatures

    if debug:
        header = f"{'Point':<25} {'Moment [kNm]':>15} {'Curvature [1/m]':>18}"
        separator = "-" * len(header)

        rows = [("Prestress", moments[0], curvatures[0] * 1000),
                ("Cracking", moments[1], curvatures[1] * 1000)]

        for i, (M, kappa) in enumerate(zip(M_extra_Nmm, kappa_extra * 1000)):
            rows.append((f"Extra Point {i + 1}", M, kappa))

        rows.append(("End of Cracking", M_eoc_Nmm, kappa_eoc * 1000))
        rows.append(("Ultimate", M_u_Nmm, kappa_u * 1000))

        print(separator)
        print(header)
        print(separator)
        for name, M, kappa in rows:
            print(f"{name:<25} {M / 1e6:>15.2f} {kappa:>18.6f}")
        print(separator)

    return mk_results

def _calculate_section_state_from_bottom_strain_sls(
        section_uls,
        eps_bot: float,
        n: float = 0.0,
        constitutive_law: str = "TENSTIFF_PARABOLIC",
        chi_scan_range: float = 1e-3,
        num_scan_points: int = 100,
        tolerance: float = 1e-2,
        ITMAX: int = 100,
        debug: bool = False,
) -> dict:
    """
    Calculate the section state (forces and strain profile) given a prescribed
    bottom fiber strain and axial force, maintaining force equilibrium.

    Fixes the bottom fiber strain to eps_bot and finds chi_y via bisection
    such that the integrated axial force equals n. My and Mz are outputs.

    Strain profile convention (consistent with rest of codebase):
        eps(z) = eps_0 + chi_y * z
        eps_bot = eps_0 + chi_y * zmin  →  eps_0 = eps_bot - chi_y * zmin

    Args:
        section_uls:            GenericSection (ULS section as input, SLS created internally)
        eps_bot:            Prescribed bottom fiber strain [-] (+ve = tension)
        n:                  Applied axial force [N] (+ve = tension, -ve = compression)
        constitutive_law:   Constitutive Law (for available const. laws see material_methods.py)
        chi_scan_range:     Half-range for initial curvature scan [1/mm] (default 1e-3)
        num_scan_points:    Number of scan points for bracketing (default 100)
        tolerance:          Force imbalance tolerance [N] for bisection (default 1e-2)
        ITMAX:              Maximum bisection iterations (default 100)
        debug:              If True, print intermediate values

    Returns:
        dict:
            - 'valid':          bool   — True if equilibrium was found
            - 'reason':         str    — failure reason if not valid
            - 'chi_y':          float  — curvature [1/mm] (-ve = sagging)
            - 'eps_0':          float  — axial strain at z=0 [-]
            - 'eps_bot':        float  — bottom fiber strain (== input) [-]
            - 'eps_top':        float  — top fiber strain [-]
            - 'n':              float  — integrated axial force [N]
            - 'm_y':            float  — integrated bending moment My [Nmm]
            - 'm_z':            float  — integrated bending moment Mz [Nmm]
            - 'strain_profile': list   — [eps_0, chi_y, 0.0]
            - 'section':        GenericSection — the SLS section used
    """

    # --- Build SLS section ---
    analysis_sec = deepcopy(sls_section_EC(section_uls, constitutive_law))

    _, _, zmin, zmax = analysis_sec.geometry.calculate_extents()

    calculator = analysis_sec.section_calculator
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    if debug:
        print(f"[calculate_curvature_from_bottom_strain]")
        print(f"  eps_bot = {eps_bot * 1000:.4f}‰  |  n = {n:.1f} N")
        print(f"  zmin = {zmin:.2f} mm  |  zmax = {zmax:.2f} mm")

    # --- Helper: build strain profile from chi_y ---
    def get_strain_profile(chi_y: float) -> list:
        eps_0 = eps_bot - chi_y * zmin
        return [eps_0, chi_y, 0.0]

    # --- Helper: integrate and return (N, My, Mz) ---
    def get_forces(chi_y: float):
        sp = get_strain_profile(chi_y)
        N, My, Mz, _ = calculator.integrator.integrate_strain_response_on_geometry(
            analysis_sec.geometry,
            sp,
            integration_data=integration_data,
            mesh_size=mesh_size,
        )
        return N, My, Mz

    # --- Phase 1: Scan to bracket the zero of (N_int - n) ---
    chi_scan = np.linspace(-chi_scan_range, chi_scan_range, num_scan_points)
    dn_scan = np.array([get_forces(chi)[0] - n for chi in chi_scan])

    crossings = [i for i in range(len(dn_scan) - 1) if dn_scan[i] * dn_scan[i + 1] < 0]

    if debug:
        print(f"  Scan found {len(crossings)} zero crossing(s) of (N_int - n)")

    if not crossings:
        return {
            'valid': False,
            'reason': (
                f"No equilibrium found in scan range "
                f"[{-chi_scan_range:.2e}, {chi_scan_range:.2e}] 1/mm. "
                f"Try increasing chi_scan_range."
            ),
        }

    # --- Phase 2: Bisect on each crossing, keep result with largest |My| ---
    best_result = None
    best_abs_my = -1.0

    for idx in crossings:
        chi_a, chi_b = chi_scan[idx], chi_scan[idx + 1]
        dn_a, dn_b = dn_scan[idx], dn_scan[idx + 1]

        for _ in range(ITMAX):
            if abs(dn_a - dn_b) < tolerance:
                break
            chi_c = (chi_a + chi_b) / 2.0
            N_c, _, _ = get_forces(chi_c)
            dn_c = N_c - n
            if dn_c * dn_a < 0:
                chi_b, dn_b = chi_c, dn_c
            else:
                chi_a, dn_a = chi_c, dn_c

        chi_final = (chi_a + chi_b) / 2.0
        N_final_N, My_final_Nmm, Mz_final_Nmm = get_forces(chi_final)
        sp = get_strain_profile(chi_final)

        if abs(My_final_Nmm) > best_abs_my:
            best_abs_my = abs(My_final_Nmm)
            best_result = {
                'valid': True,
                'n': N_final_N,
                'm_y': My_final_Nmm,
                'm_z': Mz_final_Nmm,
                'strain_profile': sp,
                'section': analysis_sec,
            }

    if debug and best_result:
        print(f"  → chi_y = {best_result['chi_y']:.6e} 1/mm")
        print(f"  → eps_top = {best_result['eps_top'] * 1000:.4f}‰")
        print(f"  → My = {best_result['m_y'] / 1e6:.3f} kNm")
        print(f"  → N residual = {best_result['n'] - n:.4f} N")

    return best_result

def calculate_prestress_forces_Nmm(section: GenericSection) -> tuple[float, float]:
    """
    Author: Elliot Melcer
    Calculate the prestressing forces.

    For each prestressed reinforcement:
    - F_p = A_s × ε_ini × E_s (prestressing force)
    - M_p = Σ(F_p × z_s) (moment from prestressing forces about centroid)

    :param section: SLS section with prestressed reinforcement
    :return: Prestressing moment [Nmm] (always positive) and total prestress force [N]
    """
    # Get section centroid
    cz = section.gross_properties.cz

    # Initialize Forces
    M_p = 0.0 # [Nmm]
    N_p = 0.0 # [N]

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

                # Add contribution to total prestress normal force
                N_p += F_p

    return abs(M_p), N_p

def _calculate_kappa_0(
    sls_sec: GenericSection,
    n: float = 0.0,
    mk_results: MomentCurvatureResults | None = None,
    m_cr_result: dict | None = None,
    debug: bool = False,
) -> float:
    """
    kappa_0 calculation for prestressed sections, used by both
    the full and simplified M-κ paths in calculate_moment_curvature_sls().

    Primary Method:
        kappa_0 = (M_p · κ_cr) / (M_cr - M_p)
        Requires valid M_cr. Source: [your reference].

    Fallback Method (only if M_cr is invalid):
        kappa_0 = -intercept / slope  (linear fit on first two pre-yield points)

        Full path (mk_np_results provided):
            Uses the first two points from the already-computed M-κ curve
            (num_pre_yield=40), so spacing is consistent with the full calculation.

        Simplified path (mk_np_results=None):
            1. find chi_yield
            2. Replicate the first 40 curvatures from full path
            3. evaluate the first two curvatures like in the full path

    :param sls_sec:     GenericSection (assumed SLS section)
    :param n:           Axial force [N]
    :param mk_results:  Pre-computed M-κ results from full path (None for simplified path)
    :param debug:       Print intermediate values
    :return:            κ₀ [1/mm]
    """

    # -----------------------------------------------------------------------
    # Check if Section is prestressed
    # -----------------------------------------------------------------------
    M_p_Nmm, _ = calculate_prestress_forces_Nmm(sls_sec)

    if M_p_Nmm == 0:
        return 0.0

    # -----------------------------------------------------------------------
    # Primary Method
    # -----------------------------------------------------------------------
    # Use pre-computed M_cr if provided, otherwise compute it
    if m_cr_result is None:
        m_cr_result = calculate_cracking_moment_sls_Nmm_EC(sls_sec, n=n)

    if m_cr_result.get('valid', True):
        M_cr     = abs(m_cr_result['m_cr'])       # Nmm
        kappa_cr = abs(m_cr_result['strain_profile'][1])  # 1/mm

        if abs(M_cr - M_p_Nmm) > 1e-3:
            kappa_0 = (M_p_Nmm * kappa_cr) / (M_cr - M_p_Nmm)

            if debug:
                print(f"[kappa_0] Method 1:"
                      f"  M_p={M_p_Nmm/1e6:.3f} kNm"
                      f"  M_cr={M_cr/1e6:.3f} kNm"
                      f"  κ_cr={kappa_cr*1000:.6f} 1/m"
                      f"  → κ₀={kappa_0*1000:.6f} 1/m")
            return kappa_0
        else:
            if debug:
                print(f"[kappa_0] Method 1: M_cr ≈ M_p, κ₀=0.0")
            return 0.0

    # -----------------------------------------------------------------------
    # Fallback Method
    # -----------------------------------------------------------------------
    if debug:
        reason = m_cr_result.get('reason', 'unknown')
        print(f"[kappa_0] M_cr invalid ({reason}) → falling back to Method 2")

    if mk_results is not None:
        # Full path: reuse first two points from already-computed curve
        chi = mk_results.chi_y[:2]
        m   = mk_results.m_y[:2]

        if debug:
            print(f"[kappa_0] Method 2 (full path): using existing M-κ points"
                  f"  χ={chi}, M={[v/1e6 for v in m]} kNm")

    else:
        # Simplified path: find chi_yield, replicate pre-yield linspace of curvatures,
        # evaluate 2 points
        calculator = sls_sec.section_calculator

        strain_yield = calculator.find_equilibrium_fixed_pivot(
            sls_sec.geometry, n, yielding=True
        )
        chi_yield = strain_yield[1]

        # Replicate chi_first logic from calculate_moment_curvature() internals
        chi_first  = 1e-8
        chi_first *= -1.0 if chi_first * chi_yield < 0 else 1.0

        # First two points of the 40-point pre-yield linspace
        chi_probe = np.linspace(chi_first, chi_yield, 40)[:2]

        res = calculator.calculate_moment_curvature(n=n, chi=chi_probe)
        chi = res.chi_y
        m   = res.m_y

        if debug:
            print(f"[kappa_0] Method 2 (simplified path): chi_yield={chi_yield*1000:.6f} 1/m"
                  f"  chi_probe={chi_probe*1000}"
                  f"  M={[v/1e6 for v in m]} kNm")

    slope, intercept = np.polyfit(chi, m, 1)

    if abs(slope) > 1e-6:
        kappa_0 = -intercept / slope
    else:
        kappa_0 = 0.0

    if debug:
        print(f"[kappa_0] Method 2: slope={slope:.4e}"
              f"  intercept={intercept:.4e}"
              f"  → κ₀={kappa_0*1000:.6f} 1/m")

    return kappa_0

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

def sls_section_EC(
        section: GenericSection,
        constitutive_law: str,
) -> GenericSection:
    """
    Author: Elliot Melcer
    Returns the section with sls constitutive law for concrete
    :param section              GenericSection (SLS or ULS)
    :param constitutive_law:    Keyword for constitutive law (for available keywords see create_sls_concrete())
    """
    # Get the geometry of the section
    geo = section.geometry

    # Create SLS Concrete from Concrete Used in Section
    conc = get_concrete(section)
    sls_conc = create_sls_concrete_EC(conc, constitutive_law)

    # Change Concrete Material
    processed_geoms = []
    for g in geo.geometries:
        processed_geoms.append(
            SurfaceGeometry.from_geometry(geo=g, new_material=sls_conc) # change concrete material
        )
    for pg in geo.point_geometries:
        processed_geoms.append(pg) # keep same reinforcement material

    new_sls_section = GenericSection(CompoundGeometry(geometries=processed_geoms), name = section.name)

    return new_sls_section

def uls_section_EC(
        section: GenericSection,
        alpha_cc: float = 0.85,
        gamma_c: float = 1.5,
) -> GenericSection:
    """
    Author: Elliot Melcer
    Returns the section with ULS constitutive law (parabola-rectangle) for concrete.
    :param section:     GenericSection (SLS or ULS)
    :param alpha_cc:    Effectiveness factor for concrete compressive strength (default: 0.85)
    :param gamma_c:     Partial safety factor for concrete (default: 1.5)
    :return:            GenericSection with ULS concrete
    """
    # Get the geometry of the section
    geo = section.geometry

    # Create SLS Concrete from Concrete Used in Section
    conc = get_concrete(section)
    uls_conc = create_uls_concrete_EC(conc, alpha_cc=alpha_cc, gamma_c=gamma_c)

    # Change Concrete Material
    processed_geoms = []
    for g in geo.geometries:
        processed_geoms.append(
            SurfaceGeometry.from_geometry(geo=g, new_material=uls_conc)  # swap concrete
        )
    for pg in geo.point_geometries:
        processed_geoms.append(pg)  # keep reinforcement unchanged

    new_uls_section = GenericSection(CompoundGeometry(geometries=processed_geoms), name=section.name)

    return new_uls_section

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