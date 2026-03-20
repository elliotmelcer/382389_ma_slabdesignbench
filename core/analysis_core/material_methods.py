"""
Author: Elliot Melcer
Internal CO2 and cost registry for materials.
"""
import numpy as np
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.constitutive_laws import Sargin, UserDefined, Elastic
from structuralcodes.materials.reinforcement import create_reinforcement

from slab_construction.floor import InsulationMaterial, InfillMaterial, ScreedMaterial

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

    # Class-level cache (shared across all uses)
    _cache: dict[object, dict[str, float]] = {}

    @classmethod
    def _register(cls, concrete) -> None:
        """Register a concrete material in the cache."""
        fck = int(round(concrete.fck))

        try:
            data = CONCRETE_CO2_TABLE[fck]
        except KeyError as exc:
            raise KeyError(
                f"No CO2/cost data available for concrete with fck = {fck}"
            ) from exc

        cls._cache[concrete] = data

    @classmethod
    def gwp(cls, concrete) -> float:
        """Returns GWP in kg CO2eq / m3."""
        if concrete not in cls._cache:
            cls._register(concrete)
        return cls._cache[concrete]["gwp"]

    @classmethod
    def cost(cls, concrete) -> float:
        """Returns cost in €/m3."""
        if concrete not in cls._cache:
            cls._register(concrete)
        return cls._cache[concrete]["cost"]


class CrackingConcreteLaw(UserDefined):
    """
    Author: Elliot Melcer

    A concrete constitutive law that handles tensile cracking correctly
    in moment-curvature analysis.

    The class overrides two methods of UserDefined with different
    responsibilities:

    get_stress(eps)
        Called by the integrator at every curvature step for every fibre.
        Returns 0 for any tensile strain beyond eps_ctm, so cracked concrete
        contributes nothing to the force resultants.  The equilibrium
        bisection then naturally shifts the neutral axis upward until the
        reinforcement closes the tension gap.

    get_ultimate_strain(yielding)
        Called by get_balanced_failure_strain() to determine chi_ultimate.
        Returns 1e6 as the positive (tensile) limit so that the concrete
        self-pairing in the double loop never produces the governing
        curvature.  chi_ultimate is therefore always governed by the
        reinforcement-concrete pair (reinf fracture vs. concrete crushing),
        which is physically correct.
    """

    def __init__(
            self,
            x: np.ndarray,
            y: np.ndarray,
            eps_ctm: float,
            eps_cu1: float,
            eps_c1: float,
            **kwargs,
    ) -> None:
        """
        Args:
            x:        Strain array passed to UserDefined (compression + tension up to eps_ctm).
            y:        Stress array passed to UserDefined.
            eps_ctm:  Cracking strain (positive).  Stress is zeroed above this.
            eps_cu1:  Ultimate compressive strain (negative).
            eps_c1:   Compressive strain at peak stress (negative), used when yielding=True.
            **kwargs: Passed through to UserDefined (e.g. name, flag).
        """
        super().__init__(x, y, **kwargs)
        self._eps_ctm = eps_ctm
        self._eps_cu1 = eps_cu1  # negative, e.g. -0.0035
        self._eps_c1 = eps_c1  # negative, e.g. -0.0020

    # ------------------------------------------------------------------
    def get_stress(self, eps):
        """
        Return stress from the parent UserDefined table, but clamp to 0
        wherever the tensile strain exceeds the cracking strain.
        """
        stress = super().get_stress(eps)

        if np.isscalar(eps):
            return 0.0 if eps > self._eps_ctm else stress

        eps = np.asarray(eps, dtype=float)
        stress = np.asarray(stress, dtype=float)
        # stress[eps > self._eps_ctm] = 0.0
        return stress

    # ------------------------------------------------------------------
    def get_ultimate_strain(self, yielding: bool = False):
        """
        Return (compressive_limit, 1e6).

        The 1e6 tensile side is intentionally unreachable so that the
        concrete self-pairing in get_balanced_failure_strain() never
        produces the minimum curvature.  chi_ultimate ends up governed
        by the reinforcement-concrete pair instead.
        """
        if yielding:
            return self._eps_c1, 1e6
        return self._eps_cu1, 1e6


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

def sargin_elastic_cracking_law(concrete: Concrete, n_c: int = 80, n_t: int = 20) -> CrackingConcreteLaw:
    """
    Author: Elliot Melcer
    Creates a Non-Linear Constitutive Law with Linear Branch in Tension + Tension Stiffening according to NAya(2006)
    and a Sargin Branch Under Compression.

    Returns a CrackingConcreteLaw Object, which returns very high tensile strain to avoid spurious failure under concrete cracking.
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
    eps_t = np.linspace(0.0, eps_ctm, n_t, endpoint=True) # dim = 1
    sig_t = Ecm * eps_t # dim = 1

    # -------------------------------
    # Tension Stiffening Points according to Naya(2006)
    # -------------------------------

    # Parameters
    P_t = 0.8
    R_t = 0.45
    S_t = 4
    F_t = 10

    eps_P_t = eps_ctm + 0.000_001 # dim = 0
    eps_S_t = S_t * eps_ctm # dim = 0
    eps_F_t = F_t * eps_ctm

    sig_P_t = P_t * sig_t[-1] # dim = 0
    sig_R_t = R_t * sig_t[-1] # dim = 0


    # -------------------------------
    # Merge safely
    # -------------------------------
    eps = np.concatenate((eps_c, eps_t, [eps_P_t], [eps_S_t], [eps_F_t]))
    sig = np.concatenate((sig_c, sig_t, [sig_P_t], [sig_R_t], [0.0]))

    # -------------------------------
    # Final safety check (important)
    # -------------------------------
    eps, unique_idx = np.unique(eps, return_index=True)
    sig = sig[unique_idx]

    return CrackingConcreteLaw(
        x=eps,
        y=sig,
        eps_ctm=eps_ctm,
        eps_cu1=eps_cu1,
        eps_c1=eps_c1,
        name="SarginCracking",
        flag=0,
    )

def get_cube(cylinder_strength) -> int:
    """
    Author: Elliot Melcer
    Return cube strength (MPa) from EN 206 concrete class table.
    """
    table = {
        12.: 15,
        16.: 20,
        20.: 25,
        25.: 30,
        30.: 37,
        35.: 45,
        40.: 50,
        45.: 55,
        50.: 60,
        55.: 67,
        60.: 75,
        70: 85,
        80: 95,
        90: 105,
        100: 115,
    }

    if cylinder_strength not in table:
        raise ValueError("Cylinder strength not in EN 206 table")

    return table[cylinder_strength]


def get_reinforcement_from_registry(
        mat_id: str,
        materials: dict,
        prestress_percent: float = 0.0,
        gamma_s: float = 1.3
):
    """
    Create a Reinforcement object from materials registry.

    Args:
        mat_id: Material identifier (e.g., "solidian GRID Q142/142-CCE-25")
        materials: Materials registry dictionary
        prestress_percent: Prestress level as percentage (0-100)
        gamma_s: Partial safety factor for reinforcement

    Returns:
        Reinforcement object

    Raises:
        KeyError: If mat_id not found in registry
        ValueError: If material type is not 'reinforcement'

    Example:
        materials = load_materials_registry("materials.csv")
        rebar = get_reinforcement_from_registry(
            "solidian GRID Q142/142-CCE-25",
            materials,
            prestress_percent=50.0
        )
    """
    if mat_id not in materials:
        raise KeyError(
            f"Material '{mat_id}' not found in materials registry. "
            f"Available reinforcement: {[k for k, v in materials.items() if v['type'] == 'reinforcement']}"
        )

    mat = materials[mat_id]

    if mat["type"] != "reinforcement":
        raise ValueError(
            f"Material '{mat_id}' has type '{mat['type']}', expected 'reinforcement'"
        )

    # Extract properties
    fyk = mat["f_yk"]  # MPa
    ftk = mat["f_tk"]  # MPa
    Es = mat["E_tex"]  # MPa
    epsuk = mat["eps_u"] / 1000  # Convert ‰ to absolute strain
    density = mat["weight"]  # kg/m³

    # Validate required properties exist
    if any(v is None for v in [fyk, ftk, Es, epsuk, density]):
        missing = [k for k, v in zip(
            ["f_yk", "f_tk", "E_tex", "eps_u", "weight"],
            [fyk, ftk, Es, mat["eps_u"], density]
        ) if v is None]
        raise ValueError(
            f"Material '{mat_id}' has missing required properties: {missing}"
        )

    # Create elastic constitutive law (CFRP is brittle - no yielding)
    britte_elastic_const_law = Elastic(Es, eps_u=epsuk)
    # britte_elastic_const_law.set_ultimate_strain(epsuk)

    # Calculate initial strain from prestress percentage
    # prestress_percent = 0.0 means no prestress
    # prestress_percent = 50.0 means prestressed to 50% of ultimate strain
    initial_strain = (prestress_percent / 100.0) * epsuk

    # Create reinforcement
    reinforcement = create_reinforcement(
        fyk=fyk,
        Es=Es,
        ftk=ftk,
        epsuk=epsuk,
        density=density,
        constitutive_law=britte_elastic_const_law,
        initial_strain=initial_strain,
        gamma_s=gamma_s,
        name=f"{mat_id}, prestressed {prestress_percent}%"
    )

    return reinforcement


def get_floor_material_from_registry(mat_id: str, materials: dict):
    """
    Create a FloorMaterial object from materials registry.

    Args:
        mat_id: Material identifier
        materials: Materials registry dictionary

    Returns:
        FloorMaterial object

    Raises:
        KeyError: If mat_id not found in registry
        ValueError: If material type is not infill/insulation/screed

    Example:
        materials = load_materials_registry("materials.csv")
        infill = get_floor_material_from_registry("generic_infill", materials)
    """
    if mat_id not in materials:
        raise KeyError(
            f"Material '{mat_id}' not found in materials registry. "
            f"Available floor materials: {[k for k, v in materials.items() if v['type'] in ['infill', 'insulation', 'screed']]}"
        )

    mat = materials[mat_id]
    expected_types = ["infill", "insulation", "screed"]

    if mat["type"] not in expected_types:
        raise ValueError(
            f"Material '{mat_id}' has type '{mat['type']}', "
            f"expected one of {expected_types}"
        )

    density = float(mat["weight"])
    if density is None:
        raise ValueError(
            f"Material '{mat_id}' missing density (weight property)"
        )

    if mat["type"] == "infill":
        return InfillMaterial(density=density, name=mat_id)
    elif mat["type"] == "screed":
        return ScreedMaterial(density=density, name=mat_id)
    else:
        E_dyn = float(mat["Edyn"])
        if E_dyn is None:
            raise ValueError(
                f"Material '{mat_id}' missing E_dyn (dynamic property)"
            )

        return InsulationMaterial(density=density, E_dyn = E_dyn, name=mat_id)

def get_material_properties(mat_id: str, materials: dict) -> dict:
    """
    Get raw material properties dictionary from registry.

    Useful for accessing GWP, cost, and other properties not needed
    for structural analysis but needed for objective function.

    Args:
        mat_id: Material identifier
        materials: Materials registry dictionary

    Returns:
        Dictionary with material properties

    Raises:
        KeyError: If mat_id not found in registry

    Example:
        mat_props = get_material_properties("solidian GRID Q142/142-CCE-25", materials)
        gwp = mat_props["gwp"]  # kg CO2-eq
        cost = mat_props["cost"]  # €/unit
    """
    if mat_id not in materials:
        raise KeyError(
            f"Material '{mat_id}' not found in materials registry. "
            f"Available: {list(materials.keys())}"
        )

    return materials[mat_id]

