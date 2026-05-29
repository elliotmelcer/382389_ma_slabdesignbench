# Registry: section_id → (geometry, concrete, reinforcement_props, reinf_area)
import numpy as np
from matplotlib import pyplot as plt
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.materials.constitutive_laws import Elastic
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_hp_sections import hp_shell_kappa_0_m2, hp_shell_c1_1_uls, hp_shell_c1_2_c50_uls, \
    hp_shell_c1_2_c80_uls, hp_shell_c1_3_uls, hp_shell_c1_4_uls
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm_EC, calculate_prestress_forces_Nmm, \
    sls_section_EC, InvalidSectionForMKError, calculate_bending_strength_sls_Nmm_EC, _ensure_force_controlled
from core.visualization_core.visualization import PlotLine, plot_moment_curvature_multiple
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell

_SHELL_REGISTRY: dict[str, HPShell] = {
    'c1_1':     hp_shell_c1_1_uls,
    'c1_2_c50': hp_shell_c1_2_c50_uls,
    'c1_2_c80': hp_shell_c1_2_c80_uls,
    'c1_3':     hp_shell_c1_3_uls,
    'c1_4':     hp_shell_c1_4_uls,
    'hp_m2':    hp_shell_kappa_0_m2,
}

def create_section_with_prestress(
    prestress_factor: float,
    _shell_id: str,
) -> GenericSection:
    """
    Creates a testing HP shell section at midspan with a variable prestress factor.
    All parameters are taken directly from the existing shell object —
    only initial_strain is overridden.

    :param _shell_id:         One of: 'c1_1', 'c1_2_c50', 'c1_2_c80', 'c1_3', 'c1_4'
    :param prestress_factor: Fraction of epsuk, e.g. 0.30 = 30% prestress
    :return:                 GenericSection at midspan (x=0.5)
    """
    if _shell_id not in _SHELL_REGISTRY:
        raise ValueError(
            f"Unknown section_id '{_shell_id}'. "
            f"Available: {list(_SHELL_REGISTRY.keys())}"
        )

    shell = _SHELL_REGISTRY[_shell_id]
    r     = shell.reinforcement

    # Rebuild a CLEAN constitutive law — r.constitutive_law is an InitialStrain
    # wrapper around the original Elastic, so reusing it would double-apply prestress.
    clean_law = Elastic(r.Es, eps_u=r.epsuk)

    reinforcement = create_reinforcement(
        fyk=r.fyk,
        Es=r.Es,
        ftk=r.ftk,
        epsuk=r.epsuk,
        density=r.density,
        constitutive_law=clean_law,                          # ← fresh, not r.constitutive_law
        gamma_s=r.gamma_s,
        initial_strain=prestress_factor * r.epsuk,
        name=f"{_shell_id} prestressed {prestress_factor * 100:.0f}%",
    )

    section = HPShell(
        shell.hp_geometry,
        shell.concrete,
        reinforcement,
        shell.reinf_area,
    ).section_at(0.5)

    return section

def _method1(section, n: float = 0.0) -> dict:
    """Method 1: kappa_0 = (M_p · κ_cr) / (M_cr - M_p)"""
    M_p, _      = calculate_prestress_forces_Nmm(section)
    M_cr_result = calculate_cracking_moment_sls_Nmm_EC(section, n=n)

    if not M_cr_result.get('valid', True):
        return {'valid': False, 'kappa_0': None,
                'M_p_kNm': M_p / 1e6, 'M_cr_kNm': None}

    M_cr     = abs(M_cr_result['m_cr'])
    kappa_cr = abs(M_cr_result['strain_profile'][1])
    kappa_0  = (M_p * kappa_cr) / (M_cr - M_p) if abs(M_cr - M_p) > 1e-3 else 0.0

    return {
        'valid':    True,
        'kappa_0':  kappa_0,
        'M_p_kNm':  M_p / 1e6,
        'M_cr_kNm': M_cr / 1e6,
        'kappa_cr': kappa_cr,
    }

def _method2(section, n: float = 0.0) -> dict:
    """Method 2: kappa_0 = -intercept / slope  (polyfit on first 2 pre-yield points)"""
    calculator = section.section_calculator

    strain_yield = calculator.find_equilibrium_fixed_pivot(section.geometry, n, yielding=True)
    chi_yield    = strain_yield[1]

    chi_first  = 1e-8
    chi_first *= -1.0 if chi_first * chi_yield < 0 else 1.0
    chi_probe  = np.linspace(chi_first, chi_yield, 40)[:2]

    res             = calculator.calculate_moment_curvature(n=n, chi=chi_probe)
    slope, intercept = np.polyfit(res.chi_y, res.m_y, 1)
    kappa_0          = -intercept / slope if abs(slope) > 1e-6 else 0.0

    return {
        'valid': True,
        'kappa_0': kappa_0,
        'slope': slope,
        'intercept': intercept
    }

def _create_moment_curvature_diagram_with_kappa_0(section: GenericSection, kappa_0: float) -> MomentCurvatureResults:
    sls_sec = sls_section_EC(section, "TENSTIFF_PARABOLIC")

    # Get bending strength strain profile
    m_u_res = calculate_bending_strength_sls_Nmm_EC(sls_sec, n=0)
    eps_0, chi_u, _ = m_u_res["strain_profile"]

    # Get curvature at cracking
    M_cr_result = calculate_cracking_moment_sls_Nmm_EC(sls_sec)
    if not M_cr_result.get("valid", True):
        raise InvalidSectionForMKError(
            f"Cannot build full M-K diagram: cracking moment invalid "
            f"({M_cr_result.get('reason', 'unknown')})"
        )
    M_cr = M_cr_result["m_cr"]
    sp = sls_sec.section_calculator.calculate_strain_profile(0, M_cr, 0)
    _, kappa_cr, _ = sp

    # Standard-chi-Array + κ_cr deterministisch einfügen
    chi_default = np.linspace(1e-8, chi_u, 40)
    chi_with_crack = np.sort(np.concatenate([chi_default, [kappa_cr]]))[::-1]  # für negative Krümmungen umkehren

    results = sls_sec.section_calculator.calculate_moment_curvature(n = 0, chi = chi_with_crack)

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

    kappa_0 = kappa_0 # <- with given kappa_0

    # -------------------------------------------------------
    # Stitch together moments and curvatures
    # -------------------------------------------------------

    # Add single initial state point at beginning
    moments_combined = np.concatenate([[0.0], results.m_y])
    curvatures_combined = np.concatenate([[kappa_0], results.chi_y])

    # Update results object
    results.m_y = moments_combined
    results.chi_y = curvatures_combined

    mon_incr_results = _ensure_force_controlled(results)
    return mon_incr_results



if __name__ == '__main__':
    for shell_id in _SHELL_REGISTRY:
        # MKD -------------------------------------------------------------------------------
        # 10 % Prestress
        section_10 = create_section_with_prestress(0.10, shell_id)
        sls_sec_10 = sls_section_EC(section_10, "TENSTIFF_PARABOLIC")

        kappa_0_10_m1 = _method1(sls_sec_10)["kappa_0"]
        kappa_0_10_m2 = _method2(sls_sec_10)["kappa_0"]

        mk_res_10_m1 = _create_moment_curvature_diagram_with_kappa_0(sls_sec_10, kappa_0_10_m1)
        mk_res_10_m2 = _create_moment_curvature_diagram_with_kappa_0(sls_sec_10, kappa_0_10_m2)

        # 60 % Prestress
        section_60 = create_section_with_prestress(0.60, shell_id)
        sls_sec_60 = sls_section_EC(section_60, "TENSTIFF_PARABOLIC")

        kappa_0_60_m1 = _method1(sls_sec_60)["kappa_0"]
        kappa_0_60_m2 = _method2(sls_sec_60)["kappa_0"]

        mk_res_60_m1 = _create_moment_curvature_diagram_with_kappa_0(sls_sec_60, kappa_0_60_m1)
        mk_res_60_m2 = _create_moment_curvature_diagram_with_kappa_0(sls_sec_60, kappa_0_60_m2)

        # Lines -------------------------------------------------------------------------------
        mk_line_10_m1 = PlotLine.from_results(mk_res_10_m1, color = "black", name = "10% prestress, method 1")
        mk_line_10_m2 = PlotLine.from_results(mk_res_10_m2, color = "grey", name = "10% prestress, method 2")

        mk_line_60_m1 = PlotLine.from_results(mk_res_60_m1, color = "red", name = "60% prestress, method 1")
        mk_line_60_m2 = PlotLine.from_results(mk_res_60_m2, color = "pink", name = "60% prestress, method 2")

        lines = [
            mk_line_10_m1,
            mk_line_10_m2,
            mk_line_60_m1,
            mk_line_60_m2,
        ]

        # Plot -------------------------------------------------------------------------------
        plot_moment_curvature_multiple(lines, ymarker=100)

    plt.show()