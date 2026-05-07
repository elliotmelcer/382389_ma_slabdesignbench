from typing import Dict, Optional

from slab_construction.slab_construction import SlabConstruction
from . import MOMENT_DATA, MAX_X_POSITIONS, MOMENT_FUNCTIONS, SystemType, MomentType
from core.analysis_core.statics.loads import Loads
from ...unit_core import *


class InternalForces:
    """
    Author: Elliot Melcer

    Utility class (not instantiable) providing methods to compute internal forces
    for various structural systems under uniform distributed load.

    Position system:
    - x = 0 at first (outer) support
    - x = 1 at next support
    - x = 2 at next support, etc.
    """

    @staticmethod
    def validate_x_position(system: SystemType, x_position: float) -> None:
        """
        Validate that x-position is within valid bounds for the given system

        :param system: Structural system type
        :param x_position: Position to validate
        :raises ValueError: If x_position is out of bounds for the system
        """

        if system not in MAX_X_POSITIONS:
            raise ValueError(
                f"Invalid system '{system}'. Must be one of: {list(MAX_X_POSITIONS.keys())}"
            )

        max_x = MAX_X_POSITIONS[system]

        if x_position < 0 or x_position > max_x:
            raise ValueError(
                f"Invalid x-position {x_position} for system '{system}'. "
                f"Must be between 0 and {max_x}."
            )

    @staticmethod
    def get_moment_data(system: SystemType, moment_type: MomentType) -> Dict[str, float]:
        """
        Get moment coefficient and x-position from lookup table

        :param system: Structural system type
        :param moment_type: Type of moment (MAX_POS_MOMENT or MAX_NEG_MOMENT)
        :return: Dictionary with 'coefficient' and 'x_position'
        """

        # Validate inputs
        if system not in MOMENT_DATA:
            raise ValueError(
                f"Invalid system '{system}'. Must be one of: {list(MOMENT_DATA.keys())}"
            )

        if moment_type not in MOMENT_DATA[system]:
            raise ValueError(
                f"Invalid moment_type '{moment_type}'. Must be 'MAX_POS_MOMENT' or 'MAX_NEG_MOMENT'"
            )

        return MOMENT_DATA[system][moment_type]

    @staticmethod
    def calculate_moment_kNm(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: SystemType = SystemType.SIMPLE_BEAM,
            combination: str = "FUNDAMENTAL",
            x_norm: Optional[float] = None,
            moment: Optional[MomentType] = None
    ) -> float:
        """
        Calculate moment at a specific position OR maximum moment for a given type in kNm

        Must provide EITHER x OR moment_type (but not both, not neither).

        :param slab_construction: Slab construction object
        :param loads: Loads object
        :param system: Structural system type
        :param combination: Load combination type
        :param x_norm: Position along beam (normalized: 0 at first support, 1 at second, etc.)
                  Use this for M(x) calculation at arbitrary position.
        :param moment: Type of moment (MAX_POS_MOMENT or MAX_NEG_MOMENT)
                           Use this for maximum moment calculation.
        :return: Moment [kNm]

        Examples:
            # Get moment at specific position (requires implemented function)
            M = calculate_moment(slab, loads, system=SystemType.SIMPLE_BEAM, x=0.3)

            # Get maximum positive moment (works for all systems via coefficient)
            M_max = calculate_moment(slab, loads, system=SystemType.THREE_SPAN, moment_type=MomentType.MAX_POS_MOMENT)
        """
        # Validate that exactly one of x or moment_type is provided
        if (x_norm is None) == (moment is None):
            raise ValueError(
                "Must provide EITHER 'x' OR 'moment_type', but not both and not neither. "
                "Use 'x' for M(x) at specific position, or 'moment_type' for maximum moment."
            )

        # Calculate span and line load (needed for both methods)
        span_m = mm_to_m(slab_construction.slab.L)
        w_line_kN_m = loads.line_load_kN_m(slab_construction, combination)

        # METHOD 1: Calculate M(x) at specific position using moment function
        if x_norm is not None:
            # Check if moment function is implemented for this system
            if system not in MOMENT_FUNCTIONS:
                raise NotImplementedError(
                    f"M(x) function not implemented for {system}. "
                    f"Available systems: {list(MOMENT_FUNCTIONS.keys())}. "
                    f"For this system, use moment_type='MAX_POS_MOMENT' or 'MAX_NEG_MOMENT' instead."
                )

            # Validate x position
            InternalForces.validate_x_position(system, x_norm)

            # Calculate position in meters
            x_m = x_norm * span_m

            # Get moment function and calculate
            moment_func = MOMENT_FUNCTIONS[system]
            moment_kNm = moment_func(x_m, w_line_kN_m, span_m)

            return moment_kNm

        # METHOD 2: Calculate maximum moment using coefficient from lookup table
        else:  # moment_type is not None
            # Get moment data from lookup table
            moment_data = InternalForces.get_moment_data(system, moment)
            coefficient = moment_data["coefficient"]

            if coefficient == 0.0:
                raise ValueError(
                    f"{moment} does not exist for {system}. "
                    f"(moment coefficient is 0.0 in lookup table)"
                )

            # Calculate moment: M = coefficient * w * L^2
            moment = coefficient * w_line_kN_m * span_m ** 2

            return moment