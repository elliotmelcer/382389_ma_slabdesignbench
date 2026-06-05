"""
Unit conversion utilities from structuralCodes (N, mm)
to common engineering units (kN, m)
"""

def mm_to_m(x: float) -> float:
    """
    Returns a length in [m] given a length in [mm]
    """
    return x * 1e-3


def mm2_to_m2(x: float) -> float:
    """
    Returns an area in [m²] given an area in [mm²]
    """
    return x * 1e-6


def mm3_to_m3(x: float) -> float:
    """
    Returns a volume in [m³] given a volume in [mm³]
    """
    return x * 1e-9


def Nmm_to_kNm(x: float) -> float:
    """
    Returns a bending moment in [kNm] given a moment in [Nmm]
    """
    return x * 1e-6


def N_to_kN(x: float) -> float:
    """
    Returns a force in [kN] given a force in [N]
    """
    return x * 1e-3
