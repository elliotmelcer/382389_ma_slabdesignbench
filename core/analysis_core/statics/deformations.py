"""
Author: Elliot Melcer
Deflection calculations using Simpson's rule and virtual work method
"""

import numpy as np
from typing import Dict, Tuple

from slab_construction.slab_construction import SlabConstruction
from core.analysis_core.loads import Loads
from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls,
    calculate_moment_curvature_sls,
    calculate_prestress_moment
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
    def calculate_deflection(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str = "SIMPLE_BEAM",
            combination: str = "QUASI-PERMANENT",
            n_intervals: int = 40,
            n_axial: float = 0.0,
            debug: bool = False
    ) -> float:
        """
        Calculate maximum deflection using Simpson's rule and virtual work method.
        Uses position-dependent M-κ curves.

        :param slab_construction: Slab construction object
        :param loads: Loads object
        :param system: Structural system type
        :param combination: Load combination for SLS
        :param n_intervals: Number of intervals for Simpson's rule (must be even)
        :param n_axial: Axial force [kN] (positive = tension)
        :param debug: Enable debug output
        :return: Maximum deflection [mm]
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

        props_support = DeflectionCalculator._get_section_properties(section_support, n_N)
        props_mid = DeflectionCalculator._get_section_properties(section_mid, n_N)

        # Setup integration points (half span due to symmetry)
        delta_x_norm = 0.5 / n_intervals # normalized
        x_positions = np.linspace(0, 0.5, n_intervals + 1)
        weights = DeflectionCalculator._simpson_weights(n_intervals)

        if debug:
            print(f"\n[DEBUG] Deflection calculation:")
            print(f"  Span: {span_m:.3f} m")
            print(f"  Support: M_cr={props_support['M_cr']:.2f} kNm, M_p={props_support['M_p']:.2f} kNm")
            print(f"  Midspan: M_cr={props_mid['M_cr']:.2f} kNm, M_p={props_mid['M_p']:.2f} kNm")

        # Calculate curvatures and integrate
        integral_sum = 0.0

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

            # Interpolate M-κ curve between support and midspan
            M_array_interp, kappa_array_interp = DeflectionCalculator._interpolate_mk_curve(
                props_support["M_array"],
                props_support["kappa_array"],
                props_mid["M_array"],
                props_mid["kappa_array"],
                x_norm
            )

            # Get applied moment at this position
            M_applied = InternalForces.calculate_moment(
                slab_construction, loads, system, combination, x_norm
            )

            # Get curvature from interpolated M-κ curve
            kappa_x = np.interp(M_applied, M_array_interp, kappa_array_interp)

            # Virtual work integration
            M_virtual_x = virtual_moment_simple_beam(x_norm, span_m)
            integral_sum += kappa_x * M_virtual_x * weight_x


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

    @staticmethod
    def _get_section_properties(
            section_uls,
            n_N: float
    ) -> Dict:
        """
        Extract complete M-κ curve and key section properties.

        :param section_uls: ULS section
        :param n_N: Axial force [N]
        :return: Dictionary with M-κ arrays and initial curvature
        """
        # Get complete M-κ curve (includes prestress branch)
        mk_result = calculate_moment_curvature_sls(
            section_uls,
            n=n_N,
            include_prestress_branch=True,
            concrete_tension=False
        )

        # Convert to positive values and proper units
        M_array = -mk_result.m_y / 1e6  # Nmm → kNm, flip to positive
        kappa_array = -mk_result.chi_y * 1000  # 1/mm → 1/m, flip to positive

        # Get cracking moment
        M_cr_result = calculate_cracking_moment_sls(section_uls, n=n_N)
        M_cr = abs(M_cr_result["m_cr"]) / 1e6  # kNm
        kappa_cr = abs(M_cr_result["strain_profile"][1]) * 1000  # 1/m

        # Get prestressing moment
        M_p = calculate_prestress_moment(section_uls)

        # Calculate initial curvature (negative = upward camber)
        if abs(M_cr - M_p) > 1e-6:
            kappa_0 = -(M_p * kappa_cr) / (M_cr - M_p)
        else:
            kappa_0 = 0.0

        return {
            "M_array": M_array,
            "kappa_array": kappa_array,
            "M_cr": M_cr,
            "kappa_cr": kappa_cr,
            "M_p": M_p,
            "kappa_0": kappa_0
        }