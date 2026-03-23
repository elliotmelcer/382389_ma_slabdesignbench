"""
Author: Elliot Melcer
Deflection calculations using Simpson's rule and virtual work method
"""

import numpy as np
from typing import Dict, Tuple

from slab_construction.slab_construction import SlabConstruction
from core.analysis_core.loads import Loads
from core.analysis_core.section_methods import (
    calculate_moment_curvature_sls,
)
from core.analysis_core.statics import virtual_moment_simple_beam
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
            system: str = "SIMPLE_BEAM",
            combination: str = "QUASI-PERMANENT",
            n_intervals: int = 40,
            n_axial: float = 0.0,
            debug: bool = False,
            extended_debug: bool = False
    ) -> float:
        """
        Calculate maximum deflection using Simpson's rule and virtual work method.
        Uses position-dependent M-κ curves.

        :param slab_construction: Slab construction object
        :param loads: Loads object
        :param system: Structural system type
        :param combination: Load combination
        :param n_intervals: Number of intervals for Simpson's rule (must be even)
        :param n_axial: Axial force [kN] (positive = tension)
        :param debug: Enable debug output
        :param extended_debug:

        :return: Maximum deflection [mm] Note: positive: sagging, negative: hogging
        """
        # Validate inputs
        if system.strip().upper() != "SIMPLE_BEAM":
            raise NotImplementedError(
                f"Deflection calculation currently only implemented for SIMPLE_BEAM"
            )
        if n_intervals % 2 != 0:
            raise ValueError("n_intervals must be even for Simpson's rule")

        # Setup
        slab = slab_construction.slab
        span_m = mm_to_m(slab.L)
        n_N = n_axial * 1000

        # Get M-κ curves at support (x=0) and midspan (x=0.5)
        section_support = slab.section_at(0.0)
        section_mid = slab.section_at(0.5)

        M_k_result_support = calculate_moment_curvature_sls(
            section_support,
            n=n_N,
            include_prestress_branch=True,
            concrete_tension=False
        )

        M_k_result_mid = calculate_moment_curvature_sls(
            section_mid,
            n=n_N,
            include_prestress_branch=True,
            concrete_tension=False
        )

        # Setup integration points (half span due to symmetry)
        delta_x_norm = 0.5 / n_intervals # normalized
        x_positions = np.linspace(0, 0.5, n_intervals + 1)
        weights = DeflectionCalculator._simpson_weights(n_intervals)

        # Calculate curvatures and integrate
        integral_sum = 0.0

        # ── Debug storage # only used if extended_debug = True
        extended_debug_rows = []

        # Iterate over all integration points
        for i, (x_norm, weight_x) in enumerate(zip(x_positions, weights)):
            # ------------------------------------------------------
            # Use Simpson Integration Method to estimate ∫ Mv(x) * κ(x)
            # ------------------------------------------------------
            # ------------------------------------------------------
            # Step 1: Find kappa(x)
            #
            #   1.1 Find kappa_load(x)
            #       1.1.1 Get interpolated M-k-curve at position x_norm
            #       1.1.2 Get real moment M(x) under load at x
            #       1.1.3 M(x) -> M-k-curve -> kappa_load(x)
            #
            #   1.2 Find kappa_0(x)
            #       1.2.1. Get first point in M-k-curve _OR_ kappa_0 = -(M_p * kappa_cr)/(M_cr - M_p)
            #
            #   1.3 Compute kappa(x) = kappa_0(x) + kappa_load(x)
            # ------------------------------------------------------

            # Parabolic interpolation factor (0 at support, 1 at midspan)

            M_array = -M_k_result_support.m_y / 1e6  # Nmm → kNm, flip to positive
            kappa_array = -M_k_result_support.chi_y * 1000  # 1/mm → 1/m, flip to positive

            # Interpolate M-κ curve between support and midspan
            M_array_interp, kappa_array_interp = DeflectionCalculator._interpolate_mk_curve(
                - M_k_result_support.m_y / 1e6,      # Nmm → kNm,  flip to positive
                - M_k_result_support.chi_y * 1000,   # 1/mm → 1/m, flip to positive
                - M_k_result_mid.m_y / 1e6,          # Nmm → kNm,  flip to positive
                - M_k_result_mid.chi_y * 1000,       # 1/mm → 1/m, flip to positive
                x_norm
            )

            # Get applied moment at this position
            M_applied = InternalForces.calculate_moment_kNm(
                slab_construction, loads, system, combination, x_norm
            )

            # Get curvature from interpolated M-κ curve
            kappa_x = np.interp(M_applied, M_array_interp, kappa_array_interp)

            # Virtual work integration
            M_virtual_x = virtual_moment_simple_beam(x_norm, span_m)
            increment = kappa_x * M_virtual_x * weight_x
            integral_sum += increment

            # ── Debug row ──────────────────────────────────────────────────────
            if extended_debug:
                extended_debug_rows.append({
                    "i": i,
                    "x_norm": x_norm,
                    "weight": weight_x,
                    "M_real": M_applied,  # kNm — no unit conversion
                    "M_virt": M_virtual_x,
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
            for r in extended_debug_rows:
                print(
                    f"{r['i']:>4} {r['x_norm']:>8.4f} {r['weight']:>8.1f} "
                    f"{r['M_real']:>12.4f} {r['M_virt']:>12.6f} "
                    f"{r['kappa']:>14.6e} {r['incr']:>14.6e} {r['cum_sum']:>14.6e}"
                )

        # Complete Simpson's rule integration
        delta_x_real = delta_x_norm * span_m
        deflection_m = (integral_sum * delta_x_real / 3) * 2  # ×2 for full span

        if debug:
            print(f"\n[DEBUG] Final deflection: {deflection_m * 1000:.2f} mm")

        return deflection_m * 1000  # Convert m to mm

    @staticmethod
    def _interpolate_mk_curve(
            M_0: np.ndarray,
            kappa_0: np.ndarray,
            M_1: np.ndarray,
            kappa_1: np.ndarray,
            x: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Interpolate between two M-κ curves.

        :param M_0: Moment array at position 0 (support)
        :param kappa_0: Curvature array at position 0 (support)
        :param M_1: Moment array at position 1 (midspan)
        :param kappa_1: Curvature array at position 1 (midspan)
        :return: Interpolated (M_array, kappa_array)
        """
        M_factor = (M_1     - M_0)      / 0.5**2
        K_factor = (kappa_1 - kappa_0)  / 0.5**2

        # Linear interpolation of both moment and curvature arrays
        M_interp        = -M_factor * (x - 0.5) ** 2 + M_1
        kappa_interp    = -K_factor * (x - 0.5) ** 2 + kappa_1


        return M_interp, kappa_interp

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

    # @staticmethod
    # def _get_section_properties(
    #         section_uls,
    #         n_N: float
    # ) -> Dict:
    #     """
    #     Extract complete M-κ curve
    #
    #     :param section_uls: ULS section
    #     :param n_N: Axial force [N]
    #     :return: Dictionary with M-κ arrays and initial curvature
    #     """
    #     # Get complete M-κ curve (includes prestress branch)
    #     mk_result = calculate_moment_curvature_sls(
    #         section_uls,
    #         n=n_N,
    #         include_prestress_branch=True,
    #         concrete_tension=False
    #     )
    #
    #     # Convert to positive values and proper units
    #     M_array = -mk_result.m_y / 1e6  # Nmm → kNm, flip to positive
    #     kappa_array = -mk_result.chi_y * 1000  # 1/mm → 1/m, flip to positive
    #
    #     return {
    #         "M_array": M_array,
    #         "kappa_array": kappa_array,
    #     }