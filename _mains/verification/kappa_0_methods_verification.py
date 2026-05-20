"""
Test: kappa_0 calculation — Method 1 vs Method 2

Method 1 (primary):  kappa_0 = (M_p · κ_cr) / (M_cr - M_p)     [from Loutfi]
Method 2 (fallback): kappa_0 = -intercept / slope              [polyfit on initial M-κ slope]

Tests:
    compare_all_methods()       — M1 vs M2 at all prestress levels, M2 always computed
                                  even when M1 is active, to assess fallback quality
    test_fallback_threshold()   — validates that M_cr becomes invalid above a threshold
                                  and that calculate_kappa_0() correctly switches to M2


Results test_fallback_threshold():

===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [C1_1]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         8.66         23.89        0.001370        0.001351        1.41           Method 1
15.0        Yes         13.00        31.28        0.002074        0.002043        1.50           Method 1
20.0        Yes         17.33        38.62        0.002794        0.002746        1.72           Method 1
25.0        Yes         21.66        45.92        0.003533        0.003461        2.01           Method 1
30.0        Yes         25.99        53.16        0.004292        0.004190        2.38           Method 1
35.0        Yes         30.32        60.36        0.005075        0.004933        2.82           Method 1
40.0        Yes         34.65        67.50        0.005885        0.005691        3.30           Method 1
45.0        Yes         38.99        74.58        0.006723        0.006467        3.82           Method 1
50.0        Yes         43.32        81.58        0.007595        0.007259        4.43           Method 1
55.0        Yes         47.65        88.52        0.008505        0.008071        5.10           Method 1
60.0        Yes         51.98        95.37        0.009459        0.008904        5.87           Method 1
65.0        Yes         56.31        102.12       0.010464        0.009758        6.74           Method 1
70.0        Yes         60.65        108.76       0.011528        0.010637        7.74           Method 1
75.0        Yes         64.98        115.27       0.012665        0.011541        8.87           Method 1

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 4.12%
    max  = 8.87%  (at 75.0% prestress)
    min  = 1.41%
===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [C1_2_C50]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         18.60        58.39        0.000555        0.000547        1.42           Method 1
15.0        Yes         27.90        74.50        0.000837        0.000825        1.33           Method 1
20.0        Yes         37.20        90.53        0.001123        0.001107        1.39           Method 1
25.0        Yes         46.49        106.48       0.001414        0.001392        1.50           Method 1
30.0        Yes         55.79        122.36       0.001710        0.001682        1.63           Method 1
35.0        Yes         65.09        138.16       0.002012        0.001975        1.86           Method 1
40.0        Yes         74.39        153.89       0.002321        0.002272        2.11           Method 1
45.0        Yes         83.69        169.54       0.002637        0.002575        2.35           Method 1
50.0        Yes         92.99        185.10       0.002961        0.002882        2.66           Method 1
55.0        Yes         102.29       200.57       0.003292        0.003193        3.02           Method 1
60.0        Yes         111.59       215.94       0.003633        0.003510        3.39           Method 1
65.0        Yes         120.89       231.21       0.003984        0.003834        3.76           Method 1
70.0        Yes         130.18       246.37       0.004346        0.004162        4.23           Method 1
75.0        Yes         139.48       261.40       0.004719        0.004494        4.78           Method 1

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 2.53%
    max  = 4.78%  (at 75.0% prestress)
    min  = 1.33%
===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [C1_2_C80]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         18.70        63.38        0.000489        0.000484        0.89           Method 1
15.0        Yes         28.05        79.68        0.000733        0.000726        0.98           Method 1
20.0        Yes         37.41        95.95        0.000979        0.000970        0.86           Method 1
25.0        Yes         46.76        112.18       0.001226        0.001216        0.82           Method 1
30.0        Yes         56.11        128.37       0.001474        0.001462        0.81           Method 1
35.0        Yes         65.46        144.53       0.001724        0.001710        0.82           Method 1
40.0        Yes         74.81        160.66       0.001976        0.001958        0.86           Method 1
45.0        Yes         84.16        176.76       0.002229        0.002209        0.92           Method 1
50.0        Yes         93.52        192.82       0.002485        0.002460        1.00           Method 1
55.0        Yes         102.87       208.86       0.002742        0.002713        1.08           Method 1
60.0        Yes         112.22       224.86       0.003003        0.002967        1.18           Method 1
65.0        Yes         121.57       240.83       0.003265        0.003223        1.29           Method 1
70.0        Yes         130.92       256.76       0.003530        0.003480        1.41           Method 1
75.0        Yes         140.27       272.65       0.003798        0.003739        1.54           Method 1

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 1.03%
    max  = 1.54%  (at 75.0% prestress)
    min  = 0.81%
===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [C1_3]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         24.32        85.98        0.000272        0.000269        0.91           Method 1
15.0        Yes         36.48        105.72       0.000408        0.000403        1.37           Method 1
20.0        Yes         48.64        125.42       0.000546        0.000538        1.49           Method 1
25.0        Yes         60.80        145.08       0.000685        0.000675        1.47           Method 1
30.0        Yes         72.96        164.70       0.000825        0.000813        1.49           Method 1
35.0        Yes         85.12        184.28       0.000967        0.000952        1.52           Method 1
40.0        Yes         97.28        203.81       0.001110        0.001092        1.62           Method 1
45.0        Yes         109.44       223.30       0.001254        0.001233        1.70           Method 1
50.0        Yes         121.60       242.75       0.001401        0.001376        1.80           Method 1
55.0        Yes         133.76       262.16       0.001549        0.001519        1.95           Method 1
60.0        Yes         145.92       281.52       0.001699        0.001665        2.04           Method 1
65.0        Yes         158.09       300.83       0.001852        0.001810        2.25           Method 1
70.0        Yes         170.25       320.09       0.002006        0.001958        2.39           Method 1
75.0        Yes         182.41       339.31       0.002163        0.002107        2.59           Method 1

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 1.76%
    max  = 2.59%  (at 75.0% prestress)
    min  = 0.91%
===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [C1_4]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         43.24        127.25       0.000439        0.000434        1.24           Method 1
15.0        Yes         64.86        163.02       0.000661        0.000654        1.19           Method 1
20.0        Yes         86.49        198.66       0.000886        0.000876        1.15           Method 1
25.0        Yes         108.11       234.16       0.001114        0.001101        1.23           Method 1
30.0        Yes         129.73       269.53       0.001346        0.001328        1.34           Method 1
35.0        Yes         151.35       304.78       0.001581        0.001558        1.45           Method 1
40.0        Yes         172.97       339.90       0.001820        0.001790        1.65           Method 1
45.0        Yes         194.59       374.89       0.002063        0.002025        1.86           Method 1
50.0        Yes         216.21       409.73       0.002311        0.002263        2.07           Method 1
55.0        Yes         237.83       444.44       0.002564        0.002505        2.32           Method 1
60.0        Yes         259.46       478.99       0.002822        0.002749        2.61           Method 1
65.0        Yes         281.08       513.37       0.003087        0.002996        2.93           Method 1
70.0        Yes         302.70       547.57       0.003357        0.003249        3.22           Method 1
75.0        Yes         324.32       581.58       0.003635        0.003505        3.59           Method 1

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 1.99%
    max  = 3.59%  (at 75.0% prestress)
    min  = 1.15%
===============================================================================================================
kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [HP_M2]
===============================================================================================================
  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]
  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]

Prestress   M_cr valid  M_p [kNm]    M_cr [kNm]   κ₀ M1 [1/m]     κ₀ M2 [1/m]     |ΔM2/M1| [%]   Active method
---------------------------------------------------------------------------------------------------------------
10.0        Yes         110.61       251.85       0.000711        0.000692        2.63           Method 1
15.0        Yes         165.92       343.59       0.001102        0.001061        3.66           Method 1
20.0        Yes         221.23       433.86       0.001524        0.001447        5.09           Method 1
25.0        Yes         276.53       522.49       0.001986        0.001853        6.71           Method 1
30.0        Yes         331.84       609.18       0.002497        0.002282        8.59           Method 1
35.0        Yes         387.15       693.50       0.003072        0.002732        11.06          Method 1
40.0        Yes         442.45       774.81       0.003734        0.003218        13.83          Method 1
45.0        Yes         497.76       852.10       0.004522        0.003733        17.46          Method 1
50.0        Yes         553.06       923.62       0.005509        0.004288        22.16          Method 1
55.0        Yes         608.37       985.83       0.006860        0.004892        28.69          Method 1
60.0        Yes         663.68       1028.62      0.009120        0.005559        39.04          Method 1
65.0        No          718.98       N/A          N/A             0.006276        N/A            Method 2 (fallback)
70.0        No          774.29       N/A          N/A             0.007097        N/A            Method 2 (fallback)
75.0        No          829.60       N/A          N/A             0.008040        N/A            Method 2 (fallback)

===============================================================================================================
SUMMARY  (deviation only where M1 is valid)
===============================================================================================================
  Method 2 vs Method 1:
    mean = 14.45%
    max  = 39.04%  (at 60.0% prestress)
    min  = 2.63%

"""

import numpy as np
from structuralcodes import set_design_code
from structuralcodes.materials.constitutive_laws import Elastic
from structuralcodes.sections import GenericSection
from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm,
    calculate_prestress_forces_Nmm,
    sls_section,
)
from _mains.testing_files.testing_hp_sections import (
    hp_shell_c1_1_uls, hp_shell_c1_2_c50_uls, hp_shell_c1_2_c80_uls,
    hp_shell_c1_3_uls, hp_shell_c1_4_uls, hp_shell_kappa_0_m2,
)
from structuralcodes.materials.reinforcement import create_reinforcement
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell



set_design_code('ec2_2004')


# ──────────────────────────────────────────────────────────────────────────────
# Section factory
# ──────────────────────────────────────────────────────────────────────────────


# Registry: section_id → (geometry, concrete, reinforcement_props, reinf_area)
_SECTION_REGISTRY: dict[str, HPShell] = {
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
    if _shell_id not in _SECTION_REGISTRY:
        raise ValueError(
            f"Unknown section_id '{_shell_id}'. "
            f"Available: {list(_SECTION_REGISTRY.keys())}"
        )

    shell = _SECTION_REGISTRY[_shell_id]
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

# ──────────────────────────────────────────────────────────────────────────────
# Local method implementations (mirrors calculate_kappa_0 internals for testing)
# ──────────────────────────────────────────────────────────────────────────────

def _method1(section, n: float = 0.0) -> dict:
    """Method 1: kappa_0 = (M_p · κ_cr) / (M_cr - M_p)"""
    M_p, _      = calculate_prestress_forces_Nmm(section)
    M_cr_result = calculate_cracking_moment_sls_Nmm(section, n=n)

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


# ──────────────────────────────────────────────────────────────────────────────
# compare_all_methods
# ──────────────────────────────────────────────────────────────────────────────

def compare_all_methods(prestress_factors: list, _shell_id: str = 'c1_1',  n: float = 0.0) -> list[dict]:
    """
    Computes kappa_0 via both methods at every prestress level.
    Method 2 is always computed — even when Method 1 is active —
    to assess its quality as a fallback.
    Deviation is |M1 - M2| / |M1| * 100.
    """

    # Column widths
    C = {
        'factor': 12,
        'valid': 12,
        'mp': 13,
        'mcr': 13,
        'k0_m1': 16,
        'k0_m2': 16,
        'dev': 15,
        'method': 14,
    }
    W = sum(C.values())
    print("=" * W)
    print(f"kappa_0 — METHOD 1 vs METHOD 2 AT ALL PRESTRESS LEVELS  [{_shell_id.upper()}]")
    print("=" * W)
    print("  M1 (primary):  (M_p · κ_cr) / (M_cr - M_p)         [Loutfi, 2023]")
    print("  M2 (fallback): -intercept / slope                  [polyfit on initial M-κ]")
    print()
    print(
        f"{'Prestress':<{C['factor']}}"
        f"{'M_cr valid':<{C['valid']}}"
        f"{'M_p [kNm]':<{C['mp']}}"
        f"{'M_cr [kNm]':<{C['mcr']}}"
        f"{'κ₀ M1 [1/m]':<{C['k0_m1']}}"
        f"{'κ₀ M2 [1/m]':<{C['k0_m2']}}"
        f"{'|ΔM2/M1| [%]':<{C['dev']}}"
        f"{'Active method':<{C['method']}}"
    )
    print("-" * W)

    results = []

    for f in prestress_factors:
        section  = create_section_with_prestress(f, _shell_id)
        sls_sec = sls_section(section, "TENSTIFF_PARABOLIC")
        r1       = _method1(sls_sec, n=n)
        r2       = _method2(sls_sec, n=n)

        m1_valid = r1['valid']
        k0_m1    = r1['kappa_0'] * 1000 if m1_valid else None   # 1/m
        k0_m2    = r2['kappa_0'] * 1000

        dev = (abs(k0_m1 - k0_m2) / abs(k0_m1) * 100
               if (k0_m1 is not None and abs(k0_m1) > 1e-9) else None)

        active = "Method 1" if m1_valid else "Method 2 (fallback)"

        def fmt(val, dec=6, w=16):
            return f"{val:<{w}.{dec}f}" if val is not None else f"{'N/A':<{w}}"

        print(
            f"{f * 100:<{C['factor']}.1f}"
            f"{'Yes' if m1_valid else 'No':<{C['valid']}}"
            f"{r1['M_p_kNm']:<{C['mp']}.2f}"
            f"{fmt(r1.get('M_cr_kNm'), 2, C['mcr'])}"
            f"{fmt(k0_m1, 6, C['k0_m1'])}"
            f"{fmt(k0_m2, 6, C['k0_m2'])}"
            f"{fmt(dev, 2, C['dev'])}"
            f"{active:<{C['method']}}"
        )

        results.append({
            'factor':     f,
            'm1_valid':   m1_valid,
            'M_p_kNm':    r1['M_p_kNm'],
            'M_cr_kNm':   r1.get('M_cr_kNm'),
            'kappa_0_m1': k0_m1,
            'kappa_0_m2': k0_m2,
            'dev_pct':    dev,
        })

    # Summary — only over rows where M1 is valid (meaningful comparison)
    comparable = [r for r in results if r['m1_valid'] and r['dev_pct'] is not None]
    print()
    print("=" * W)
    print("SUMMARY  (deviation only where M1 is valid)")
    print("=" * W)
    if comparable:
        devs    = [r['dev_pct'] for r in comparable]
        worst   = max(comparable, key=lambda r: r['dev_pct'])
        print(f"  Method 2 vs Method 1:")
        print(f"    mean = {np.mean(devs):.2f}%")
        print(f"    max  = {np.max(devs):.2f}%  (at {worst['factor']*100:.1f}% prestress)")
        print(f"    min  = {np.min(devs):.2f}%")
    else:
        print("  No comparable results.")

    return results


# ──────────────────────────────────────────────────────────────────────────────
# test_fallback_threshold  (pytest)
# ──────────────────────────────────────────────────────────────────────────────

FACTORS = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]

# def test_fallback_threshold(_shell_id: str = 'hp_m2'):
#     """
#     Validates two things:
#
#     1. M_cr validity transitions from True → False at some threshold, never back.
#        This confirms the threshold is real and monotone.
#
#     2. calculate_kappa_0() returns a positive, finite value at every prestress
#        level — regardless of whether M1 or M2 is active.
#        This confirms the fallback is correctly triggered and produces a usable result.
#     """
#
#     print("\n" + "=" * 90)
#     print(f"FALLBACK THRESHOLD TEST  [{_shell_id.upper()}]")
#     print("=" * 90)
#     print(f"  Validates M_cr validity transition and calculate_kappa_0() output at each level.")
#     print()
#     print(f"{'Prestress':<12} {'M_cr valid':<13} {'κ₀ [1/m]':<18} {'Method active':<20} {'Pass'}")
#     print("-" * 90)
#
#     threshold_found    = False
#     threshold_factor   = None
#     seen_invalid_then_valid = False
#
#     for f in FACTORS:
#         section     = create_section_with_prestress(f, _shell_id)
#         sls_sec     = sls_section(section, "TENSTIFF_PARABOLIC")
#         m_cr_result = calculate_cracking_moment_sls_Nmm(sls_sec)
#         m1_valid    = m_cr_result.get('valid', True)
#
#         # Track threshold
#         if not m1_valid and not threshold_found:
#             threshold_found  = True
#             threshold_factor = f
#         if m1_valid and threshold_found:
#             seen_invalid_then_valid = True   # would mean non-monotone — bad
#
#         # Call the actual unified function
#         kappa_0      = _calculate_kappa_0(sls_sec)
#         method_active = "Method 1" if m1_valid else "Method 2 (fallback)"
#
#         is_finite   = np.isfinite(kappa_0)
#         # after
#         NUMERICAL_ZERO = 1e-9  # 1/mm — below this is floating point noise, not a real result
#         is_positive = kappa_0 > -NUMERICAL_ZERO
#         is_meaningful = abs(kappa_0) > NUMERICAL_ZERO
#         row_pass = is_finite and is_positive
#
#         print(
#             f"{f * 100:<12.1f}"
#             f"{'Yes' if m1_valid else 'No':<13}"
#             f"{kappa_0 * 1000:<18.6f}"
#             f"{method_active:<20}"
#             f"{'✓' if row_pass else '✗  ← FAIL'}"
#             f"{'  ⚠ near-zero' if not is_meaningful else ''}"
#         )
#
#         assert is_finite,   f"kappa_0 is not finite at {f*100:.0f}% prestress"
#         assert is_positive, f"kappa_0 <= 0 at {f*100:.0f}% prestress (got {kappa_0:.6e})"
#
#     print()
#     assert not seen_invalid_then_valid, \
#         "M_cr validity is non-monotone: became valid again after turning invalid"
#
#     if threshold_found:
#         print(f"  ✓ [{_shell_id}] M_cr becomes invalid at {threshold_factor*100:.0f}% prestress — Method 2 activates correctly.")
#     else:
#         print(f"  ✓ [{_shell_id}] M_cr valid at all tested levels — Method 1 used throughout, fallback not needed.")
#
#     print(f"  ✓ [{_shell_id}] calculate_kappa_0() returns finite positive value at all prestress levels.")
#

# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    factors = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75]

    for shell_id in _SECTION_REGISTRY:
        # shell_id = 'c1_2_c80'
        compare_all_methods(factors, shell_id)

    # test_fallback_threshold()