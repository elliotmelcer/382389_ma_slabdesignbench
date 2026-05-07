from collections.abc import Callable
from typing import Dict
from enum import Enum

from core.analysis_core.statics.internal_forces import InternalForces
from core.analysis_core.statics.loads import Loads
from core.unit_core import mm_to_m
from slab_construction.slab_construction import SlabConstruction

"""
Enum Class for types of systems
"""
class SystemType(str, Enum):
    CANTILEVER = "CANTILEVER"
    SIMPLE_BEAM = "SIMPLE_BEAM"
    TWO_SPAN = "TWO_SPAN"
    THREE_SPAN = "THREE_SPAN"
    FOUR_SPAN = "FOUR_SPAN"
    FIVE_SPAN = "FIVE_SPAN"

"""
Enum Class for available types moments
"""
class MomentType(str, Enum):
    MAX_POS_MOMENT = "MAX_POS_MOMENT"
    MAX_NEG_MOMENT = "MAX_NEG_MOMENT"

"""
Moment functions M(x) for systems where full distribution is implemented
Signature: (x_m: float, w: float, L: float) -> float
where x_m is position in meters, w is line load in kN/m, L is span in meters
"""
MOMENT_FUNCTIONS: Dict[SystemType, Callable[[float, float, float], float]] = {
    SystemType.SIMPLE_BEAM: InternalForces.moment_simple_beam,
    SystemType.CANTILEVER: InternalForces.moment_cantilever,
    SystemType.TWO_SPAN: InternalForces.moment_two_span,
}

"""
Maximum valid x-position for each system type
x = 0 at first support, x = 1 at second support, etc.

  |-> x
  0      0.5      1      1.5      2

  ====================================|...
 /_\             /_\             /_\
"""

MAX_X_POSITIONS: Dict[str, float] = {
    "CANTILEVER": 1.0,    # From support (0) to free end (1)
    "SIMPLE_BEAM": 1.0,   # From support 0 to support 1
    "TWO_SPAN": 2.0,      # Supports at 0, 1, 2
    "THREE_SPAN": 3.0,    # Supports at 0, 1, 2, 3
    "FOUR_SPAN": 4.0,     # Supports at 0, 1, 2, 3, 4
    "FIVE_SPAN": 5.0,     # Supports at 0, 1, 2, 3, 4, 5
}


"""
 Lookup table for moment coefficients and x-positions
 M = coefficient * w * L^2
 x_position: location where max moment occurs
"""
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


