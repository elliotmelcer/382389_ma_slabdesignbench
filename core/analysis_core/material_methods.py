"""
Author: Elliot Melcer
Internal CO2 and cost registry for materials.
"""
import numpy as np
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.constitutive_laws import Sargin, UserDefined

# ---------------------------------------------------------------------------
# Internal data table (source: Beton.xlsx, internalised)
# ---------------------------------------------------------------------------

CONCRETE_CO2_TABLE: dict[int, dict[str, float]] = {
    12:  {"gwp": 140.0, "cost": 70.0},
    16:  {"gwp": 159.0, "cost": 72.5},
    20:  {"gwp": 178.0, "cost": 75.0},
    25:  {"gwp": 197.0, "cost": 80.0},
    30:  {"gwp": 219.0, "cost": 85.0},
    35:  {"gwp": 244.0, "cost": 90.0},
    40:  {"gwp": 265.0, "cost": 100.0},
    45:  {"gwp": 286.0, "cost": 110.0},
    50:  {"gwp": 300.0, "cost": 120.0},
    55:  {"gwp": 314.0, "cost": 130.0},
    60:  {"gwp": 328.0, "cost": 140.0},
    70:  {"gwp": 342.0, "cost": 150.0},
    80:  {"gwp": 356.0, "cost": 160.0},
    90:  {"gwp": 370.0, "cost": 170.0},
    100: {"gwp": 384.0, "cost": 180.0},
}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ConcreteCO2Registry:
    """Registry for CO2 and cost data of EC2 concrete materials."""

    __slots__ = ("_cache",)

    def __init__(self):
        # Key: concrete instance, Value: {"gwp": ..., "cost": ...}
        self._cache: dict[object, dict[str, float]] = {}

    def _register(self, concrete) -> None:
        fck = int(round(concrete.fck))

        try:
            data = CONCRETE_CO2_TABLE[fck]
        except KeyError as exc:
            raise KeyError(
                f"No CO2/cost data available for concrete with fck = {fck}"
            ) from exc

        self._cache[concrete] = data

    def gwp(self, concrete) -> float:
        """Returns GWP in kg CO2eq / m3."""
        if concrete not in self._cache:
            self._register(concrete)
        return self._cache[concrete]["gwp"]

    def cost(self, concrete) -> float:
        """Returns cost in €/m3."""
        if concrete not in self._cache:
            self._register(concrete)
        return self._cache[concrete]["cost"]


def sargin_elastic_law(concrete: Concrete, n_c: int = 80, n_t: int = 20) -> UserDefined:
    """
    Author: Elliot Melcer
    Creates a Non-Linear Constitutive Law with Linear Branch in Tension and Sargin Branch Under Compression
    - Compression: Sargin (eps_cu1 → eps_c1)
    - Tension: linear elastic (0 → eps_ctm)
    """

    # -------------------------------
    # Read parameters
    # -------------------------------
    fcm = concrete.fcm
    Ecm = concrete.Ecm
    fctm = concrete.fctm

    eps_c1 = -abs(concrete.eps_c1)
    eps_cu1 = -abs(concrete.eps_cu1)
    k = concrete.k_sargin

    eps_ctm = fctm / Ecm

    # -------------------------------
    # Sargin compression
    # -------------------------------
    sargin = Sargin(
        fc=fcm,
        eps_c1=eps_c1,
        eps_cu1=eps_cu1,
        k=k,
    )

    # ⚠ exclude zero explicitly
    eps_c = np.linspace(eps_cu1, 0.00, n_c, endpoint=True)
    eps_c = eps_c[eps_c < 0.0]
    sig_c = sargin.get_stress(eps_c)

    # -------------------------------
    # Elastic tension
    # -------------------------------
    eps_t = np.linspace(0.0, eps_ctm, n_t, endpoint=True)
    sig_t = Ecm * eps_t

    # -------------------------------
    # Merge safely
    # -------------------------------
    eps = np.concatenate((eps_c, eps_t))
    sig = np.concatenate((sig_c, sig_t))

    # -------------------------------
    # Final safety check (important)
    # -------------------------------
    eps, unique_idx = np.unique(eps, return_index=True)
    sig = sig[unique_idx]

    return UserDefined(
        x=eps,
        y=sig,
        name="SarginElastic",
        flag=0,
    )

def get_cube(cylinder_strength) -> float:
    """
    Author: Elliot Melcer
    Return cube strength (MPa) from EN 206 concrete class table.
    """
    table = {
        12.: 15.,
        16.: 20.,
        20.: 25.,
        25.: 30.,
        30.: 37.,
        35.: 45.,
        40.: 50.,
        45.: 55.,
        50.: 60.,
        55.: 67.,
        60.: 75.,
        70: 85,
        80: 95,
        90: 105,
        100: 115,
    }

    if cylinder_strength not in table:
        raise ValueError("Cylinder strength not in EN 206 table")

    return table[cylinder_strength]

