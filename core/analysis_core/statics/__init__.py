from collections.abc import Callable
from typing import Dict
from enum import Enum
from core.analysis_core.statics.loads import Loads
from core.unit_core import mm_to_m
from slab_construction.slab_construction import SlabConstruction


class SystemType(str, Enum):
    CANTILEVER = "CANTILEVER"
    SIMPLE_BEAM = "SIMPLE_BEAM"
    TWO_SPAN = "TWO_SPAN"
    THREE_SPAN = "THREE_SPAN"
    FOUR_SPAN = "FOUR_SPAN"
    FIVE_SPAN = "FIVE_SPAN"


class MomentType(str, Enum):
    MAX_POS_MOMENT = "MAX_POS_MOMENT"
    MAX_NEG_MOMENT = "MAX_NEG_MOMENT"

# Maximum valid x-position for each system type
# x = 0 at first support, x = 1 at second support, etc.
#
#   |-> x
#   0      0.5      1      1.5      2
#
#   ====================================|...
#  /_\             /_\             /_\
#
MAX_X_POSITIONS: Dict[str, float] = {
    "CANTILEVER": 1.0,    # From support (0) to free end (1)
    "SIMPLE_BEAM": 1.0,   # From support 0 to support 1
    "TWO_SPAN": 2.0,      # Supports at 0, 1, 2
    "THREE_SPAN": 3.0,    # Supports at 0, 1, 2, 3
    "FOUR_SPAN": 4.0,     # Supports at 0, 1, 2, 3, 4
    "FIVE_SPAN": 5.0,     # Supports at 0, 1, 2, 3, 4, 5
}

# Lookup table for moment coefficients and x-positions
# M = coefficient * w * L^2
# x_position: location where max moment occurs
MOMENT_DATA: Dict[str, Dict[str, Dict[str, float]]] = {
    "CANTILEVER": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.000,
            "x_position": 0.0,       # N/A, MAX_POS_MOMENT caught as error
        },
        "MAX_NEG_MOMENT": {
            "coefficient": -0.500,
            "x_position": 0.0,
        },
    },
    "SIMPLE_BEAM": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.125,
            "x_position": 0.5,
        },
        "MAX_NEG_MOMENT": {
            "coefficient": 0.000,
            "x_position": 0.0,       # N/A MAX_NEG_MOMENT caught as error
        },
    },
    "TWO_SPAN": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.070,
            "x_position": 0.390,       # from Stab2D-NL Analysis
        },
        "MAX_NEG_MOMENT": {
            "coefficient": -0.125,
            "x_position": 1.0,
        },
    },
    "THREE_SPAN": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.080,
            "x_position": 0.404,       # from Stab2D-NL Analysis
        },
        "MAX_NEG_MOMENT": {
            "coefficient": -0.100,
            "x_position": 1.0,
        },
    },
    "FOUR_SPAN": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.077,
            "x_position": 0.404,       # from Stab2D-NL Analysis
        },
        "MAX_NEG_MOMENT": {
            "coefficient": -0.107,
            "x_position": 1.0,
        },
    },
    "FIVE_SPAN": {
        "MAX_POS_MOMENT": {
            "coefficient": 0.078,
            "x_position": 0.404,       # from Stab2D-NL Analysis
        },
        "MAX_NEG_MOMENT": {
            "coefficient": -0.105,
            "x_position": 1.0,
        },
    },
}

def calculate_line_load_kN_m(
        slab_construction: SlabConstruction,
        loads: Loads,
        combination: str = "FUNDAMENTAL"
) -> float:
    """
    Calculate line load from surface load.

    Shared utility function for internal forces and deflection calculations.

    :param slab_construction: Slab construction object
    :param loads: Loads object
    :param combination: Load combination type
    :return: Line load in kN/m
    """
    width_m = mm_to_m(slab_construction.slab.B)
    combination = combination.strip().upper()

    if combination == "FUNDAMENTAL":
        area_load_kN_m2 = loads.fundamental_combination_kN_m2(slab_construction)
    elif combination == "FREQUENT":
        area_load_kN_m2 = loads.frequent_combination_kN_m2(slab_construction)
    elif combination in ("QUASI-PERMANENT", "QUASI_PERMANENT", "QUASI PERMANENT"):
        area_load_kN_m2 = loads.quasi_permanent_combination_kN_m2(slab_construction)
    elif combination == "RARE":
        area_load_kN_m2 = loads.rare_combination_kN_m2(slab_construction)
    else:
        raise ValueError(
            "Invalid combination. Must be one of: 'FUNDAMENTAL', 'RARE', 'FREQUENT' or 'QUASI-PERMANENT'."
        )

    line_load_kN_m = area_load_kN_m2 * width_m

    return line_load_kN_m

def moment_simple_beam(x: float, w: float, L: float) -> float:
    """
    Calculate moment at position x for a simple beam.

    :param x: Position along beam [m]
    :param w: Uniformly distributed load [kN/m]
    :param L: Span length [m]
    :return: Moment at x [kNm]
    """
    return w * x * (L - x) / 2

def moment_two_span(x, w, L):
    if not (0 <= x <= 2*L):
        return 0

    xi = L - x if x <= L else x - L

    return w * (xi**2 / 2 - 5 * L * xi / 8 + L**2 / 8)

def virtual_moment_simple_beam(x_norm: float, span_m: float) -> float:
    """
    Calculate virtual moment for unit load at midspan of simple beam.

    :param x_norm: Normalized position along beam (0 at first support, 0.5 at midspan)
    :param span_m: Span length [m]
    :return: Virtual moment [m] (moment arm for unit load)
    """
    return x_norm * span_m / 2

# Moment functions M(x) for systems where full distribution is implemented
# Signature: (x_m: float, w: float, L: float) -> float
# where x_m is position in meters, w is line load in kN/m, L is span in meters
MOMENT_FUNCTIONS: Dict[str, Callable[[float, float, float], float]] = {
    "SIMPLE_BEAM": moment_simple_beam,
    "CANTILEVER": lambda x_m, w, L: -w * x_m**2 / 2,
    "TWO_SPAN": moment_two_span,
}