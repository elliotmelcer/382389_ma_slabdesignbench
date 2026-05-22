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
    calculate_moment_curvature_sls_EC, calculate_cracking_moment_sls_Nmm_EC,
)
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.internal_forces import InternalForces
from core.unit_core import mm_to_m


class DeflectionCalculator:
    """
    Calculate deflections using Simpson's rule and virtual work method.
    Uses position-dependent M-κ curves (calculated at support and midspan).

    Position convention: x is normalized (0 at first support, 1 at second support, etc.)
    """

    @staticmethod
    def calculate_deflection_mm_EC(
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
                    "FACTOR_EC"    load history considered according to Eurocode 2, Chapter 7.4.3, Equation (7.18)
                    # "SECANT"    load history considered according to Kreller (1989)*, Chapter 4.2.4
                    #
                    # *Title: "Zum nichtlinearen Trag- und Verformungsverhalten von Stahlbetonstabtragwerken unter Last- und Zwangeinwirkung"

        :param m_k_simplification:  Control simplified M-K-Diagram Calculation
                                    For available inputs see _simplified_moment_curvature_method() in section_methods.py
        :param constitutive_law:    Control Concrete Material Behavior in SLS
                                    for available inputs see sls_concrete() in material_methods.py
        :param slab_construction:   Slab construction object
        :param loads:               Loads object
        :param system:              Structural system type
        :param combination:         Load combination (Ignored when load_history_method='FACTOR_EC')
        :param n_intervals:         Number of intervals for Simpson's rule (must be even)
        :param N_axial_N:           Axial force [N] (positive = tension)
        :param debug:               Enable debug output
        :param extended_debug:      Enable extended debug output

        :return: Maximum deflection [mm] Note: positive: sagging, negative: hogging
        """
        # --------------------------
        # Normalize Input
        # --------------------------

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
        if combination not in ("FUNDAMENTAL", "QUASI-PERMANENT", "FREQUENT", "RARE"):
            raise ValueError("combination must be 'FUNDAMENTAL', 'QUASI-PERMANENT', 'FREQUENT' or 'RARE'")

        # --------------------------
        # Shared Input kwargs
        # --------------------------
        deflection_kwargs = dict(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            n_intervals=n_intervals,
            N_axial_N=N_axial_N,
            m_k_simplification=m_k_simplification,
            debug=debug,
            extended_debug=extended_debug,
        )

        # --------------------------
        # Consider Load History
        # --------------------------
        if load_history_method == "NONE":
            # Use Direct Calculation Method
            deflection_mm = DeflectionCalculator._direct_deflection_method(
                combination=combination,
                constitutive_law = constitutive_law,
                **deflection_kwargs
            )

        elif load_history_method == "FACTOR_EC":
            deflection_mm = DeflectionCalculator._factor_deflection_method(
                **deflection_kwargs
            )

        # elif load_history_method == "SECANT":
        #     # deflection_m = DeflectionCalculator._secant_deflection_method()
        #     deflection_mm = 0.0

        else:
            raise ValueError("load_history_method must be 'NONE' or 'FACTOR_EC'")

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
        # --------------------------
        # Setup
        # --------------------------
        span_m = mm_to_m(slab_construction.slab.L)

        # Calculate Kappas along the Beam
        kappa_array, kappa_debug = DeflectionCalculator._get_interpolated_kappa_array(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            combination=combination,
            n_intervals=n_intervals,
            N_axial_N=N_axial_N,
            constitutive_law = constitutive_law,
            m_k_simplification = m_k_simplification,
        )

        # Real Moments at integration points
        M_applied_array_kNm = kappa_debug["M_applied_kNm"]

        # Integrate using Simpson's Method
        deflection_mm, simpson_debug  = DeflectionCalculator._simpson_integration(
            span_m=span_m,
            n_intervals=n_intervals,
            M_applied_array_kNm = M_applied_array_kNm,
            kappa_array=kappa_array,
        )

        if extended_debug:
            DeflectionCalculator._print_kappa_interp_debug(kappa_debug)
            DeflectionCalculator._print_simpson_debug(simpson_debug)

        return deflection_mm

    @staticmethod
    def _factor_deflection_method(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType,
            n_intervals: int,
            N_axial_N: float,
            m_k_simplification,
            debug: bool,
            extended_debug: bool
    ) -> float:

        # --------------------------
        # Setup
        # --------------------------
        span_m = mm_to_m(slab_construction.slab.L)
        # Interpolation points (half span due to symmetry)
        x_positions = np.linspace(0, 0.5, n_intervals + 1)

        # Shared args for both κ-array calls
        kappa_kwargs = dict(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            combination="QUASI-PERMANENT",
            n_intervals=n_intervals,
            N_axial_N=N_axial_N,
            m_k_simplification=m_k_simplification,
        )

        # --------------------------
        # Curvatures Fully Cracked
        # --------------------------
        kappa_array_fully_cracked, kappa_cracked_debug = DeflectionCalculator._get_interpolated_kappa_array(
            constitutive_law = "NONE_PARABOLIC",
            **kappa_kwargs
        )

        # --------------------------
        # Curvatures Fully Uncracked
        # --------------------------
        kappa_array_fully_uncracked, kappa_uncracked_debug = DeflectionCalculator._get_interpolated_kappa_array(
            constitutive_law="ELASTIC_ELASTIC",
            **kappa_kwargs
        )

        # --------------------------
        # Zeta Calculation
        # --------------------------
        zeta_array, zeta_debug = DeflectionCalculator._calculate_zeta_array(
            slab_construction=slab_construction,
            loads=loads,
            system=system,
            N_axial_N=N_axial_N,
            x_positions=x_positions,
        )
        m_real_array_kNm = zeta_debug["m_qp_kNm"] # Use quasi-permanent combination for integration
        m_cr_interp_list_kNm = zeta_debug["m_cr_interp_kNm"]

        # -----------------------------
        # Weighted Curvatures
        # -----------------------------
        kappa_weighted_array = DeflectionCalculator._calculate_weighted_kappa(
            kappa_array_fully_cracked=kappa_array_fully_cracked,
            kappa_array_fully_uncracked=kappa_array_fully_uncracked,
            zeta_array=zeta_array
        )

        # -----------------------------
        # Simpson Integration
        # -----------------------------
        deflection_weighted_mm, simpson_debug = DeflectionCalculator._simpson_integration(
            span_m=span_m,
            n_intervals=n_intervals,
            M_applied_array_kNm=m_real_array_kNm,
            kappa_array=kappa_weighted_array
        )

        if debug:
            print(f"M_cr_array: {m_cr_interp_list_kNm}")
            print(f"zeta_array: {zeta_array}")
        if extended_debug:
            DeflectionCalculator._print_kappa_interp_debug(kappa_cracked_debug, label="cracked")
            DeflectionCalculator._print_kappa_interp_debug(kappa_uncracked_debug, label="uncracked")
            DeflectionCalculator._print_zeta_debug(zeta_array, zeta_debug)
            DeflectionCalculator._print_simpson_debug(simpson_debug)

        return deflection_weighted_mm


    # @staticmethod
    # def _secant_deflection_method():
    #     # 1. Calculate M-K-Line at Support and Midsection
    #     # 2. Determine (M_real, kappa_real) at every point along the beam using rare combination
    #     # 3. Linearly interpolate down to quasi permanent combination
    #     #       - use prestress point or (0,0)
    #     #       - mind max slope determined by fully cracked section
    #     return None

    @staticmethod
    def _simpson_integration(
            span_m: float,
            n_intervals: int,
            M_applied_array_kNm: list[float],
            kappa_array: list[float],
    ) -> tuple[float, dict[str, list]]:
        """
        Integrate δ = ∫ M_v(x)·κ(x) dx over the half-span using Simpson's rule,
        then double by symmetry.
        :return: (deflection_mm, debug_info) where debug_info holds per-point
                 arrays aligned with the Simpson points.
        """
        # Setup integration points (half span due to symmetry)
        delta_x_norm = 0.5 / n_intervals  # normalized
        x_positions = np.linspace(0, 0.5, n_intervals + 1)
        weights = DeflectionCalculator._simpson_weights(n_intervals)

        # Calculate curvatures and integrate
        integral_sum = 0.0

        # Store detailed Simpson Point Information
        # Per-station debug arrays
        weight_list: list[float] = []
        m_virtual_list: list[float] = []
        increment_list: list[float] = []
        cum_sum_list: list[float] = []

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
            M_virtual_x_kNm = DeflectionCalculator._virtual_moment(x_norm, span_m)

            # 3. Virtual work integration
            increment = kappa_x * M_virtual_x_kNm * weight_x
            integral_sum += increment

            # Store detailed Simpson Point Information
            weight_list.append(float(weight_x))
            m_virtual_list.append(M_virtual_x_kNm)
            increment_list.append(increment)
            cum_sum_list.append(integral_sum)

        # Complete Simpson's rule integration for full span
        delta_x_real = delta_x_norm * span_m
        deflection_m = (integral_sum * delta_x_real / 3) * 2  # ×2 for full span
        deflection_mm = deflection_m * 1000 # Convert m to mm

        debug_info = {
            "x_positions": list(x_positions),
            "weights": weight_list,
            "M_real_kNm": list(M_applied_array_kNm),
            "M_virtual": m_virtual_list,
            "kappa": list(kappa_array),
            "increment": increment_list,
            "cum_sum": cum_sum_list,
        }

        return deflection_mm, debug_info

    @staticmethod
    def _print_simpson_debug(simpson_debug: dict[str, list]) -> None:
        header = (
            f"{'i':>4} {'x_norm':>8} {'weight':>8} {'M_real[kNm]':>12} "
            f"{'M_virt':>12} {'kappa[1/m]':>14} {'increment':>14} {'cum_sum':>14}"
        )
        print("\n[DEBUG] Simpson integration points (0 → 0.5):")
        print(header)
        print("-" * len(header))
        for i, (x, w, m_r, m_v, k, incr, cs) in enumerate(zip(
                simpson_debug["x_positions"],
                simpson_debug["weights"],
                simpson_debug["M_real_kNm"],
                simpson_debug["M_virtual"],
                simpson_debug["kappa"],
                simpson_debug["increment"],
                simpson_debug["cum_sum"],
        )):
            print(
                f"{i:>4} {x:>8.4f} {w:>8.1f} {m_r:>12.4f} {m_v:>12.6f} "
                f"{k:>14.6e} {incr:>14.6e} {cs:>14.6e}"
            )

    @staticmethod
    def _calculate_zeta_array(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType,
            N_axial_N: float,
            x_positions: np.ndarray,
            beta: float = 0.5,
    ) -> tuple[list[float], dict[str, list[float]]]:
        """
        Distribution coefficient ζ along the half-span per EC2 (7.19) under rare combination:
            ζ = 1 - β · (M_cr / M)²   if M > M_cr
            ζ = 0                     otherwise

        M_cr is parabolically interpolated between the support and midspan
        sections. Used by EC2 (7.18) to weight cracked vs uncracked curvature:
            κ = ζ · κ_cracked + (1 - ζ) · κ_uncracked

        :param x_positions: Normalized Simpson stations along half-span (0 → 0.5)
        :param beta: Load-duration factor (0.5 short-term, 1.0 sustained/cyclic)
        :return: (zeta_array, debug_info) where debug_info holds the per-station
                 interpolated cracking moment and the applied moment, both as
                 lists aligned with x_positions.
        """
        slab = slab_construction.slab

        # Cracking moments at support and midspan: Nmm → kNm, flipped to positive
        m_cr_support_kNm = -calculate_cracking_moment_sls_Nmm_EC(
            slab.section_at(0.0), n=N_axial_N
        )["m_cr"] / 1e6
        m_cr_mid_kNm = -calculate_cracking_moment_sls_Nmm_EC(
            slab.section_at(0.5), n=N_axial_N
        )["m_cr"] / 1e6

        zeta_array: list[float] = []
        m_cr_interp_list_kNm: list[float] = []
        m_rare_list_kNm: list[float] = []
        m_qp_list_kNm: list[float] = []

        for x_norm in x_positions:
            # Cracking moment at this station
            m_cr_kNm = DeflectionCalculator._parabolic_interpolate(
                m_cr_support_kNm,
                m_cr_mid_kNm,
                x_norm
            )

            # Quasi-Permanent moment for debug info
            m_qp_kNm = InternalForces.calculate_moment_kNm(
                slab_construction,
                loads,
                system,
                "QUASI-PERMANENT",
                x_norm
            )

            # Cracking state under rare combination, used for zeta calculation
            m_rare_kNm = InternalForces.calculate_moment_kNm(
                slab_construction,
                loads,
                system,
                "RARE",
                x_norm
            )

            # EC2 (7.19): Use rare combination to determine cracking state of structure
            if m_rare_kNm > m_cr_kNm:
                zeta = 1.0 - beta * (m_cr_kNm / m_rare_kNm) ** 2
                zeta = max(0.0, min(1.0, zeta))
            else:
                zeta = 0.0

            zeta_array.append(zeta)
            m_cr_interp_list_kNm.append(m_cr_kNm)
            m_rare_list_kNm.append(m_rare_kNm)
            m_qp_list_kNm.append(m_qp_kNm)

        debug_info = {
            "x_positions": list(x_positions),
            "m_cr_interp_kNm": m_cr_interp_list_kNm,
            "m_rare_kNm": m_rare_list_kNm,
            "m_qp_kNm": m_qp_list_kNm,
        }

        return zeta_array, debug_info

    @staticmethod
    def _print_zeta_debug(zeta_array: list[float], zeta_debug: dict[str, list]) -> None:
        header = (
            f"{'i':>4} {'x_norm':>8} {'M_rare':>10} {'M_qp':>10} "
            f"{'M_cr':>10} {'zeta':>8}"
        )
        print("\n[DEBUG] Zeta calculation (0 → 0.5):")
        print(header)
        print("-" * len(header))
        for i, (x, m_rare, m_qp, m_cr, z) in enumerate(zip(
                zeta_debug["x_positions"],
                zeta_debug["m_rare_kNm"],
                zeta_debug["m_qp_kNm"],
                zeta_debug["m_cr_interp_kNm"],
                zeta_array,
        )):
            print(f"{i:>4} {x:>8.4f} {m_rare:>10.4f} {m_qp:>10.4f} {m_cr:>10.4f} {z:>8.4f}")

    @staticmethod
    def _calculate_weighted_kappa(
            kappa_array_fully_cracked: list[float],
            kappa_array_fully_uncracked: list[float],
            zeta_array: list[float]
    ) -> list[float]:
        """
        Returns a list of zeta weighted kappas according to EC2 Eq. (7.18)
        :param kappa_array_fully_cracked:   list of curvatures for a fully cracked structure
        :param kappa_array_fully_uncracked: list of curvatures for a fully uncracked structure
        :param zeta_array:                  list of factors for weighting cracked and uncracked curvatures
        :return:
        """
        kappa_weighted_array = []

        for k_cr, k_uncr, zeta in zip(kappa_array_fully_cracked, kappa_array_fully_uncracked, zeta_array):
            # Weighted Kappa according to EC2 Eq. (7.18)
            kappa_weighted = zeta * k_cr + (1 - zeta) * k_uncr
            kappa_weighted_array.append(kappa_weighted)

        return kappa_weighted_array

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
    ) -> tuple[list[float], dict[str, list]]:
        """
        Compute κ(x) at each Simpson point by parabolically interpolating the M-κ curve
        between support and midspan, then looking up κ at the applied moment.
        """
        # Slab
        slab = slab_construction.slab
        # Setup integration points (half span due to symmetry)
        x_positions = np.linspace(0, 0.5, n_intervals + 1)

        # M-k-curves at support and midspan
        M_k_result_support = calculate_moment_curvature_sls_EC(
            slab.section_at(0.0),
            n=N_axial_N,
            constitutive_law = constitutive_law,
            simplification= m_k_simplification
        )

        M_k_result_mid = calculate_moment_curvature_sls_EC(
            slab.section_at(0.5),
            n=N_axial_N,
            constitutive_law = constitutive_law,
            simplification= m_k_simplification
        )

        # Calculate real Moment at integration points
        M_applied_array_kNm = [
            InternalForces.calculate_moment_kNm(
                slab_construction,
                loads,
                system,
                combination,
                x
            )
            for x in x_positions
        ]

        kappas = []

        # Debug arrays
        m_applied_list = []
        m_low_list = []
        m_high_list = []
        kappa_low_list = []
        kappa_high_list = []

        for x_norm, M_applied_kNm in zip(x_positions, M_applied_array_kNm):
            # Compute interpolated M-k-curve at position x_norm
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

            # Linear Interpolation within M-k-diagram
            kappa_x = float(np.interp(M_applied_kNm, M_array_interp_kNm, kappa_array_interp))
            kappas.append(kappa_x)

            # Record the bracketing points used for the lookup
            M_low, M_high, kappa_low, kappa_high = DeflectionCalculator._interpolation_bounds(
                M_applied_kNm, M_array_interp_kNm, kappa_array_interp
            )
            m_applied_list.append(M_applied_kNm)
            m_low_list.append(M_low)
            m_high_list.append(M_high)
            kappa_low_list.append(kappa_low)
            kappa_high_list.append(kappa_high)

        debug_info = {
            "x_positions": list(x_positions),
            "M_applied_kNm": m_applied_list,
            "M_low": m_low_list,
            "M_high": m_high_list,
            "kappa_low": kappa_low_list,
            "kappa_high": kappa_high_list,
        }

        return kappas, debug_info

    @staticmethod
    def _print_kappa_interp_debug(kappa_debug: dict[str, list], label: str = "") -> None:
        header = (
            f"{'x_norm':>8} {'M_applied_kNm':>14} {'M_low':>12} {'M_high':>12} "
            f"{'kappa_low':>14} {'kappa_high':>14}"
        )
        title = "[DEBUG] κ-interpolation bounds"
        if label:
            title = f"{title} ({label})"
        print(f"\n{title}:")
        print(header)
        print("-" * len(header))
        for x, m_a, m_lo, m_hi, k_lo, k_hi in zip(
                kappa_debug["x_positions"],
                kappa_debug["M_applied_kNm"],
                kappa_debug["M_low"],
                kappa_debug["M_high"],
                kappa_debug["kappa_low"],
                kappa_debug["kappa_high"],
        ):
            print(
                f"{x:>8.4f} {m_a:>14.4f} {m_lo:>12.4f} {m_hi:>12.4f} "
                f"{k_lo:>14.6e} {k_hi:>14.6e}"
            )

    @staticmethod
    def _interpolation_bounds(x, xs, ys):
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
        """
        Performs parabolic interpolation between y_0 and y_1 at x_norm
        Source: Loutfi 2022
        :param y_0:     Function value at x_0
        :param y_1:     Function value at x_1
        :param x_norm:  Normalized x value
        :return:
        """
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

    @staticmethod
    def _virtual_moment(x_norm: float, span_m: float) -> float:
        """
        Calculate virtual moment for unit load at midspan of simple beam.

        :param x_norm: Normalized position along beam (0 at first support, 0.5 at midspan)
        :param span_m: Span length [m]
        :return: Virtual moment [m] (moment arm for unit load)
        """
        return x_norm * span_m / 2