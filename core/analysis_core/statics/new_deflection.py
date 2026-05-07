"""
Author: Elliot Melcer
Deflection calculations
"""

import numpy as np
from typing import Any, Union

from core import normalize_input
from slab_construction.slab_construction import SlabConstruction
from core.analysis_core.statics.loads import Loads
from core.analysis_core.section_methods import (
    calculate_moment_curvature_sls, calculate_cracking_moment_sls_Nmm,
)
from core.analysis_core.statics import virtual_moment_unit_load_at_midspan_simple_beam, SystemType
from core.analysis_core.statics.internal_forces import InternalForces
from core.unit_core import mm_to_m


class DeflectionCalculator:
    """
    Calculate deflections using Simpson's rule and virtual work method.
    Uses position-dependent M-κ curves (calculated at support and midspan).

    Position convention: x is normalized (0 at first support, 1 at second support, etc.)
    """

    @staticmethod
    def calculate_deflection_mm(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType = SystemType.SIMPLE_BEAM,
            combination: str = "QUASI-PERMANENT",
            n_intervals: int = 40,
            N_axial_N: float = 0.0,
            constitutive_law: str = "TENSTIFF_PARABOLIC",
            load_history_method: str = "NONE",
            m_k_simplification = False,
            debug: bool = False,
            extended_debug: bool = False
    ) -> float:
        """
        Calculate maximum deflection using Simpson's rule and virtual work method.
        Uses position-dependent M-κ curves.

        :param load_history_method:
                    Input       Explanation
                    ------------------------------------------------------------------------------------------------
                    "NONE"      no load history considered, direct method used with parameter combination
                    "FACTOR"    load history considered according to Eurocode 2, Chapter 7.4.3, Equation (7.18)
                    "SECANT"    load history considered according to Kreller (1989)*, Chapter 4.2.4

                    *Title: "Zum nichtlinearen Trag- und Verformungsverhalten von Stahlbetonstabtragwerken unter Last- und Zwangeinwirkung"

        :param m_k_simplification:  Control simplified M-K-Diagram Calculation
                                    For available inputs see _simplified_moment_curvature_method() in section_methods.py
        :param constitutive_law:    Control Concrete Material Behavior in SLS
                                    for available inputs see sls_concrete() in material_methods.py
        :param slab_construction:   Slab construction object
        :param loads:               Loads object
        :param system:              Structural system type
        :param combination:         Load combination
        :param n_intervals:         Number of intervals for Simpson's rule (must be even)
        :param N_axial_N:           Axial force [N] (positive = tension)
        :param debug:               Enable debug output
        :param extended_debug:      Enable extended debug output

        :return: Maximum deflection [mm] Note: positive: sagging, negative: hogging
        """
        # --------------------------
        # Normalize Input
        # --------------------------

        system = normalize_input(system)
        combination = normalize_input(combination)
        load_history_method = normalize_input(load_history_method)
        constitutive_law = normalize_input(constitutive_law)

        # --------------------------
        # Validate inputs
        # --------------------------
        if system != SystemType.SIMPLE_BEAM:
            raise NotImplementedError(
                f"Deflection calculation currently only implemented for SIMPLE_BEAM"
            )
        if n_intervals % 2 != 0:
            raise ValueError("n_intervals must be even for Simpson's rule")
        if combination not in ("FUNDAMENTAL", "QUASI_PERMANENT", "FREQUENT", "RARE"):
            raise ValueError("combination must be 'FUNDAMENTAL', 'QUASI_PERMANENT', 'FREQUENT' or 'RARE'")

        # --------------------------
        # Consider Load History
        # --------------------------
        if load_history_method == "NONE":
            # Use Direct Calculation Method
            deflection_mm = DeflectionCalculator._direct_deflection_method(
                slab_construction=slab_construction,
                loads=loads,
                system=system,
                combination=combination,
                n_intervals=n_intervals,
                N_axial_N=N_axial_N,
                constitutive_law = constitutive_law,
                m_k_simplification = m_k_simplification,
                debug=debug,
                extended_debug=extended_debug,
            )

        elif load_history_method == "FACTOR":
            deflection_mm = DeflectionCalculator._factor_deflection_method(
                slab_construction=slab_construction,
                loads=loads,
                system=system,
                combination=combination,
                n_intervals=n_intervals,
                N_axial_N=N_axial_N,
                m_k_simplification=m_k_simplification,
                debug=debug,
                extended_debug=extended_debug,
            )

        elif load_history_method == "SECANT":
            # deflection_m = DeflectionCalculator._secant_deflection_method()
            deflection_mm = 0.0

        else:
            raise ValueError("load_history_method must be 'NONE', 'FACTOR' or 'SECANT'")

        return deflection_mm

    @staticmethod
    def _direct_deflection_method(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType,
            combination: str,
            n_intervals: int,
            N_axial_N: float,
            constitutive_law: str,
            m_k_simplification,
            debug: bool,
            extended_debug: bool
    ) -> float:
        # Span
        span_m = mm_to_m(slab_construction.slab.L)

        # Calculate Kappas along the Beam
        kappa_array = DeflectionCalculator._get_interpolated_kappa_array(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            combination=combination,
            n_intervals=n_intervals,
            N_axial_N=N_axial_N,
            constitutive_law = constitutive_law,
            m_k_simplification = m_k_simplification,
            debug = debug,
            extended_debug = extended_debug,
        )

        # Setup integration points (half span due to symmetry)
        x_positions = np.linspace(0, 0.5, n_intervals + 1)

        # Calculate real Moment at integration points
        M_applied_array_kNm = [
            InternalForces.calculate_moment_kNm(slab_construction, loads, system, combination, x)
            for x in x_positions
        ]

        # Integrate using Simpson's Method
        deflection_mm, _ = DeflectionCalculator._simpson_integration(
            span_m=span_m,
            n_intervals=n_intervals,
            M_applied_array_kNm = M_applied_array_kNm,
            kappa_array=kappa_array,
            debug=debug,
            extended_debug=extended_debug,
        )

        return deflection_mm

    @staticmethod
    def _factor_deflection_method(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType,
            combination: str,
            n_intervals: int,
            N_axial_N: float,
            m_k_simplification,
            debug: bool,
            extended_debug: bool
    ) -> float:

        # Setup
        slab = slab_construction.slab
        span_m = mm_to_m(slab.L)

        # Get sections at support (x=0) and midspan (x=0.5)
        section_support = slab.section_at(0.0)
        section_mid = slab.section_at(0.5)

        # --------------------------
        # Curvatures Fully Cracked
        # --------------------------

        kappa_array_fully_cracked = DeflectionCalculator._get_interpolated_kappa_array(
            slab_construction = slab_construction,
            loads = loads,
            system = system,
            combination = combination,
            n_intervals = n_intervals,
            N_axial_N = N_axial_N,
            constitutive_law = "NONE_PARABOLIC",
            m_k_simplification=m_k_simplification,
            debug = debug
        )

        # --------------------------
        # Curvatures Fully Uncracked
        # --------------------------

        kappa_array_fully_uncracked = DeflectionCalculator._get_interpolated_kappa_array(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            combination=combination,
            n_intervals=n_intervals,
            N_axial_N=N_axial_N,
            constitutive_law="ELASTIC_ELASTIC",
            m_k_simplification = m_k_simplification,
            debug = debug
        )

        # --------------------------
        # Zeta Calculation
        # --------------------------

        # Cracking Moment at Support
        m_cr_result_support = calculate_cracking_moment_sls_Nmm(
            section_support,
            n=N_axial_N,
        )
        m_cr_support = m_cr_result_support["m_cr"]

        # Cracking Moment at Mid-Span
        m_cr_result_mid = calculate_cracking_moment_sls_Nmm(
            section_mid,
            n=N_axial_N,
        )
        m_cr_mid = m_cr_result_mid["m_cr"]

        # Setup Interpolation points (half span due to symmetry)
        x_positions = np.linspace(0, 0.5, n_intervals + 1)

        # Cracking Moment along the Beam (Debugging)
        m_cr_interp_list_kNm = []

        # Real Moment along the Beam (Debugging)
        m_real_list_kNm = []

        # Zeta Array
        zeta_array = []

        for x_norm in x_positions:
            # Cracking Moment at x_norm
            m_cr_x_norm_kNm = DeflectionCalculator._parabolic_interpolate(
                - m_cr_support / 1e6,   # Nmm → kNm,  flip to positive
                - m_cr_mid / 1e6,       # Nmm → kNm,  flip to positive
                x_norm
            )

            # Real Moment at x_norm
            m_real_x_kNm = InternalForces.calculate_moment_kNm(
                slab_construction,
                loads,
                combination = combination, #TODO: Should this be "RARE" combination?
                system = system,
                x_norm = x_norm)

            # Weight Factor Zeta according to EC2 Eq. (7.19)
            beta = 0.5 # short term load

            if m_real_x_kNm > m_cr_x_norm_kNm:
                zeta_x_norm = 1 - beta * (m_cr_x_norm_kNm / m_real_x_kNm)**2
                zeta_x_norm = max(0.0, min(1.0, zeta_x_norm))
            else:
                zeta_x_norm = 0.0

            # Append to Lists for debugging
            m_cr_interp_list_kNm.append(m_cr_x_norm_kNm)
            m_real_list_kNm.append(m_real_x_kNm)
            zeta_array.append(zeta_x_norm)

        # -----------------------------
        # Weighted Curvatures
        # -----------------------------

        kappa_weighted_array = []

        for k_cr, k_uncr, zeta in zip(kappa_array_fully_cracked, kappa_array_fully_uncracked, zeta_array):
            # Weighted Kappa according to EC2 Eq. (7.18)
            kappa_weighted = zeta * k_cr + (1 - zeta) * k_uncr
            kappa_weighted_array.append(kappa_weighted)

        # -----------------------------
        # Simpson Integration
        # -----------------------------
        deflection_weighted_mm, _ = DeflectionCalculator._simpson_integration(
            span_m=span_m,
            n_intervals=n_intervals,
            M_applied_array_kNm=m_real_list_kNm,
            kappa_array=kappa_weighted_array,
            debug=debug,
            extended_debug=extended_debug,
        )

        if debug:
            print(f"M_cr_array: {m_cr_interp_list_kNm}")
            print(f"zeta_array: {zeta_array}")

        return deflection_weighted_mm


    @staticmethod
    def _secant_deflection_method():
        # TODO
        # 1. Calculate M-K-Line at Support and Midsection
        # 2. Determine (M_real, kappa_real) at every point along the beam using rare combination
        # 3. Linearly interpolate down to quasi permanent combination
        #       - use prestress point or (0,0)
        #       - mind max slope determined by fully cracked section
        return None

    @staticmethod
    def  _simpson_integration(
            span_m: float,
            n_intervals: int,
            M_applied_array_kNm: list[float],
            kappa_array: list[float],
            debug: bool,
            extended_debug: bool,
    ) -> tuple[float, list[dict[str, Any]]]:

        # Setup integration points (half span due to symmetry)
        delta_x_norm = 0.5 / n_intervals  # normalized
        x_positions = np.linspace(0, 0.5, n_intervals + 1)
        weights = DeflectionCalculator._simpson_weights(n_intervals)

        # Calculate curvatures and integrate
        integral_sum = 0.0

        # Store detailed Simpson Point Information
        extended_simpson_output = []

        # Iterate over all integration points
        for i, (x_norm, weight_x) in enumerate(zip(x_positions, weights)):
            # ----------------------------------------------------------
            # Use Simpson Integration Method to estimate ∫ Mv(x) * κ(x)
            #
            # 1. Find Curvature at x
            # 2. Find Virtual Moment at x
            # 3. Virtual work integration for half span
            # ----------------------------------------------------------

            # 1. Find Curvature at x
            M_applied_kNm = M_applied_array_kNm[i]
            kappa_x = kappa_array[i]

            # 2. Find Virtual Moment at x
            M_virtual_x_kNm = DeflectionCalculator._virtual_moment_unit_load_at_midspan_simple_beam(x_norm, span_m)

            # 3. Virtual work integration
            increment = kappa_x * M_virtual_x_kNm * weight_x
            integral_sum += increment

            # Store detailed Simpson Point Information
            extended_simpson_output.append({
                "i": i,
                "x_norm": x_norm,
                "weight": weight_x,
                "M_real": M_applied_kNm,
                "M_v": M_virtual_x_kNm,
                "kappa": kappa_x,
                "incr": increment,
                "cum_sum": integral_sum,
            })

        # ── Print extended debug table ──────────────────────────────────────────────────
        if extended_debug:
            header = (
                f"{'i':>4} {'x_norm':>8} {'weight':>8} {'M_real[kNm]':>12} "
                f"{'M_virt':>12} {'kappa[1/m]':>14} {'increment':>14} {'cum_sum':>14}"
            )
            print("\n[DEBUG] Simpson integration points (0 → 0.5):")
            print(header)
            print("-" * len(header))
            for r in extended_simpson_output:
                print(
                    f"{r['i']:>4} {r['x_norm']:>8.4f} {r['weight']:>8.1f} "
                    f"{r['M_real']:>12.4f} {r['M_v']:>12.6f} "
                    f"{r['kappa']:>14.6e} {r['incr']:>14.6e} {r['cum_sum']:>14.6e}"
                )

        # Complete Simpson's rule integration for full span
        delta_x_real = delta_x_norm * span_m
        deflection_m = (integral_sum * delta_x_real / 3) * 2  # ×2 for full span
        deflection_mm = deflection_m * 1000 # Convert m to mm

        return deflection_mm, extended_simpson_output

    @staticmethod
    def _virtual_moment_unit_load_at_midspan_simple_beam(x_norm: float, span_m: float) -> float:
        """
        Calculate virtual moment for unit load at midspan of simple beam.

        :param x_norm: Normalized position along beam (0 at first support, 0.5 at midspan)
        :param span_m: Span length [m]
        :return: Virtual moment [m] (moment arm for unit load)
        """
        return x_norm * span_m / 2

    @staticmethod
    def _get_interpolated_kappa_array(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType,
            combination: str,
            n_intervals: int,
            N_axial_N: float,
            constitutive_law: str,
            m_k_simplification,
            debug: bool = False,
            extended_debug: bool = False,
    ) -> list[float]:
        """
        Compute κ(x) at each position by parabolically interpolating the M-κ curve
        between support and midspan, then looking up κ at the applied moment.
        """
        # Slab
        slab = slab_construction.slab

        # Get sections at support (x=0) and midspan (x=0.5)
        section_support = slab.section_at(0.0)
        section_mid = slab.section_at(0.5)

        M_k_result_support = calculate_moment_curvature_sls(
            section_support,
            n=N_axial_N,
            constitutive_law = constitutive_law,
            m_k_simplification = m_k_simplification
        )
        #
        # if debug:
        #     print("M_k_result_support")
        #     print(M_k_result_support.m_y)
        #     print(M_k_result_support.chi_y)

        M_k_result_mid = calculate_moment_curvature_sls(
            section_mid,
            n=N_axial_N,
            constitutive_law = constitutive_law,
            m_k_simplification = m_k_simplification
        )
        #
        # if debug:
        #     print("M_k_result_mid")
        #     print(M_k_result_mid.m_y)
        #     print(M_k_result_mid.chi_y)

        # Setup integration points (half span due to symmetry)
        x_positions = np.linspace(0, 0.5, n_intervals + 1)

        # Calculate real Moment at integration points
        M_applied_array_kNm = [
            InternalForces.calculate_moment_kNm(slab_construction, loads, system, combination, x)
            for x in x_positions
        ]

        kappas = []

        interp_bounds_output = []

        for x_norm, M_applied_kNm in zip(x_positions, M_applied_array_kNm):
            # -------------------------------------------------------
            # 1. Get interpolated M-k-curve at position x_norm
            # 2. Get real moment M(x) under load at x
            # 3. M(x) -> interpolated M-k-curve -> kappa(x)
            # --------------------------------------------------------

            M_array_interp_kNm = DeflectionCalculator._parabolic_interpolate(
                -M_k_result_support.m_y / 1e6,
                -M_k_result_mid.m_y / 1e6,
                x_norm
            )

            kappa_array_interp = DeflectionCalculator._parabolic_interpolate(
                -M_k_result_support.chi_y * 1000,
                -M_k_result_mid.chi_y * 1000,
                x_norm
            )

            M_low, M_high, kappa_low, kappa_high = DeflectionCalculator.interp_bounds(
                M_applied_kNm,
                M_array_interp_kNm,
                kappa_array_interp
            )

            interp_bounds_output.append({
                "x_norm": x_norm,
                "M_applied_kNm": M_applied_kNm,
                "M_low": M_low,
                "M_high": M_high,
                "kappa_low": kappa_low,
                "kappa_high": kappa_high,
            })

            kappas.append(np.interp(M_applied_kNm, M_array_interp_kNm, kappa_array_interp))

        # ── Print extended debug table ─────────────────────────────────────────────
        if extended_debug:
            header = (
                f"{'x_norm':>8} {'M_applied_kNm':>12} {'M_low':>12} {'M_high':>12} "
                f"{'kappa_low':>14} {'kappa_high':>14}"
            )
            print("\n[DEBUG] Interpolation bounds:")
            print(header)
            print("-" * len(header))
            for r in interp_bounds_output:
                print(
                    f"{r['x_norm']:>8.4f} "
                    f"{r['M_applied_kNm']:>12.4f} "
                    f"{r['M_low']:>12.4f} "
                    f"{r['M_high']:>12.4f} "
                    f"{r['kappa_low']:>14.6e} "
                    f"{r['kappa_high']:>14.6e}"
                )



        return kappas

    @staticmethod
    def interp_bounds(x, xs, ys):
        """
        Return (x_lo, x_hi, y_lo, y_hi) such that:
        x_lo <= x <= x_hi and y values come from same indices.

        xs must be sorted.
        """
        xs = np.asarray(xs)
        ys = np.asarray(ys)

        i = np.searchsorted(xs, x)

        i_lo = max(i - 1, 0)
        i_hi = min(i, len(xs) - 1)

        return xs[i_lo], xs[i_hi], ys[i_lo], ys[i_hi]

    @staticmethod
    def _parabolic_interpolate(
            y_0: Union[float, np.ndarray],
            y_1: Union[float, np.ndarray],
            x_norm: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        factor = (y_1- y_0)  / 0.5 ** 2
        y_interp = -factor * (x_norm - 0.5) ** 2 + y_1

        return y_interp

    @staticmethod
    def _simpson_weights(n: int) -> np.ndarray:
        """
        Calculate Simpson's rule weights: [1, 4, 2, 4, 2, ..., 4, 1]

        :param n: Number of intervals (must be even)
        :return: Array of weights
        """
        weights = np.ones(n + 1)
        weights[1:-1:2] = 4  # Odd indices
        weights[2:-1:2] = 2  # Even indices (except first and last)
        return weights