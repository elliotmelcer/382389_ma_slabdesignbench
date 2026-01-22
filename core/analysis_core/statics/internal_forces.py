from typing import Dict

from slab_construction.slab_construction import SlabConstruction
from . import MOMENT_DATA, MAX_X_POSITIONS  # Relative import from the package
from ..loads import Loads
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
    def _calculate_line_load(
            slab_construction: SlabConstruction,
            loads: Loads,
            combination: str = "FUNDAMENTAL"
    ) -> float:
        """
        Helper method to calculate line load from surface load

        :param slab_construction: Slab construction object
        :param loads: Loads object
        :param combination: Load combination type
        :return: Line load in kN/m
        """
        width = mm_to_m(slab_construction.slab.B)

        # for easier user behavior: accepts "FUNDAMENTAL", "fundamental" or "  Fundamental  "
        combination = combination.strip().upper()

        if combination == "FUNDAMENTAL":
            w = loads.fundamental_combination(slab_construction)  # kN/m2
        elif combination == "FREQUENT":
            w = loads.frequent_combination(slab_construction)  # kN/m2
        elif combination in ("QUASI-PERMANENT", "QUASI_PERMANENT", "QUASI PERMANENT"):
            w = loads.quasi_permanent_combination(slab_construction)  # kN/m2
        else:
            raise ValueError(
                "Invalid combination. Must be one of: 'FUNDAMENTAL', 'FREQUENT', 'QUASI-PERMANENT'."
            )

        # Convert surface load [kN/m2] to line load [kN/m] using slab width
        return w * width

    @staticmethod
    def validate_x_position(system: str, x_position: float) -> None:
        """
        Validate that x-position is within valid bounds for the given system

        :param system: Structural system type
        :param x_position: Position to validate
        :raises ValueError: If x_position is out of bounds for the system
        """
        system = system.strip().upper()

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
    def get_moment_data(system: str, moment_type: str) -> Dict[str, float]:
        """
        Get moment coefficient and x-position from lookup table

        :param system: Structural system type
        :param moment_type: Type of moment (MAX_POS_MOMENT or MAX_NEG_MOMENT)
        :return: Dictionary with 'coefficient' and 'x_position'
        """
        # Normalize inputs
        system = system.strip().upper()
        moment_type = moment_type.strip().upper()

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
    def calculate_moment(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str = "SIMPLE_BEAM",
            moment_type: str = "MAX_POS_MOMENT",
            combination: str = "FUNDAMENTAL"
    ) -> float:
        """
        General method to calculate moment for any system and moment type

        :param slab_construction: Slab construction object
        :param loads: Loads object
        :param system: Structural system type
        :param moment_type: Type of moment (MAX_POS_MOMENT or MAX_NEG_MOMENT)
        :param combination: Load combination type
        :return: Moment in kNm
        """
        # Get moment data from lookup table
        moment_data = InternalForces.get_moment_data(system, moment_type)
        coefficient = moment_data["coefficient"]

        if coefficient == 0.0:
            raise ValueError(
                f"{moment_type} does not exist for {system}. "
                f"(moment coefficient is 0.0 in lookup table)"
            )

        # Calculate span and line load
        span = mm_to_m(slab_construction.slab.L)
        w_line = InternalForces._calculate_line_load(slab_construction, loads, combination)

        # Calculate moment: M = coefficient * w * L^2
        moment = coefficient * w_line * span ** 2

        return moment