
from typing import Union

import numpy as np
from structuralcodes.materials.concrete import Concrete, create_concrete
from structuralcodes.materials.constitutive_laws import Sargin, UserDefined, Elastic
from structuralcodes.materials.reinforcement import create_reinforcement

from slab_construction.floor import InsulationMaterial, InfillMaterial, ScreedMaterial

class CrackingConcreteLawEC(UserDefined):
    """
    Author: Elliot Melcer

    A concrete constitutive law that handles tensile cracking correctly
    in moment-curvature analysis according to Eurocode.

    The class overrides get_ultimate_strain of UserDefined to allow for cracking:

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
            strains: np.ndarray,
            stresses: np.ndarray,
            eps_cu1: float,
            eps_c1: float,
            **kwargs,
    ) -> None:
        """
        Args:
            strains:  Strain array passed to UserDefined
            stresses: Stress array passed to UserDefined
            eps_ctm:  Cracking strain (positive).  Stress is zeroed above this.
            eps_cu1:  Ultimate compressive strain (negative).
            eps_c1:   Compressive strain at peak stress (negative), used when yielding=True.
            **kwargs: Passed through to UserDefined (e.g. name, flag).
        """
        super().__init__(strains, stresses, **kwargs)
        self._eps_cu1 = eps_cu1  # negative, e.g. -0.0035
        self._eps_c1 = eps_c1  # negative, e.g. -0.0020

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

class TensionStiffeningConcreteLawEC(CrackingConcreteLawEC):
    """
    Author: Elliot Melcer
    A concrete constitutive law that handles tension stiffening
    """

    def __init__(
            self,
            strains: np.ndarray,
            stresses: np.ndarray,
            eps_cu1: float,
            eps_c1: float,
            **kwargs,
    ) -> None:
        """
        Args:
            strains:  Strain array passed to UserDefined
            stresses: Stress array passed to UserDefined
            eps_cu1:  Ultimate compressive strain (negative).
            eps_c1:   Compressive strain at peak stress (negative), used when yielding=True.
            **kwargs: Passed through to UserDefined (e.g. name, flag).
        """
        super().__init__(strains, stresses, eps_cu1, eps_c1, **kwargs)
        self.eps_F_t = strains[-1]
        self.eps_S_t = strains[-2]

def create_sls_concrete_EC(conc: Union[Concrete, float, int], constitutive_law: str) -> Concrete:
    """
    Creates an SLS Concrete object with new constitutive law according to Eurocode
    Available constitutive law keywords: NONE_PARABOLIC, FCTM_PARABOLIC, TENSTIFF_PARABOLIC, ELASTIC_ELASTIC
    :param conc: Concrete object or fck value
    :param constitutive_law: constitutive law (by keyword)
    :return:
    """
    f_ck = conc.fck if isinstance(conc, Concrete) else float(conc)
    f_cube = get_cube_EC(f_ck)

    # Normalize Input
    constitutive_law_normalized = constitutive_law.strip().upper().replace("-", "_").replace(" ", "_")

    # If Concrete should be able to take tension forces, use custom constitutive law (linear in tension and non-linear in compression)
    if constitutive_law_normalized == "NONE_PARABOLIC":
        sls_conc = create_concrete(fck=f_ck,
                                       constitutive_law='sargin',
                                       name=f"C{f_ck}/{f_cube} SLS")
    elif constitutive_law_normalized == "FCTM_PARABOLIC":
        sls_conc = create_concrete(fck=f_ck,
                                   constitutive_law=fctm_parabolic_law_EC(conc),
                                   name=f"C{f_ck}/{f_cube} SLS")
    elif constitutive_law_normalized == "TENSTIFF_PARABOLIC":
        sls_conc = create_concrete(fck=f_ck,
                                   constitutive_law=tenstiff_parabolic_law_EC(conc),
                                   name=f"C{f_ck}/{f_cube} SLS")
    elif constitutive_law_normalized == "ELASTIC_ELASTIC":
        sls_conc = create_concrete(fck=f_ck,
                                       constitutive_law='elastic',
                                       name=f"C{f_ck}/{f_cube} SLS")
    else:
        raise ValueError(
            f"{constitutive_law_normalized} is not a valid constitutive law. Available types (Tension / Compression):\n"
            f"     NONE_PARABOLIC:     Can't take tension, compression parabolic acc. to Sargin\n"
            f"     FCTM_PARABOLIC:     Linear elastic until fctm in tension, compression parabolic acc. to Sargin\n"
            f"     TENSTIFF_PARABOLIC: Linear elastic until fctm, then tension stiffening*, compression parabolic acc. to Sargin\n"
            f"     ELASTIC_ELASTIC:    Elastic in tension and compression without cracking or breaking")

    return sls_conc

def create_uls_concrete_EC(conc: Union[Concrete, float, int],
                           alpha_cc: float = 0.85,
                           gamma_c: float = 1.5) -> Concrete:
    """
    Author: Elliot Melcer
    Creates a ULS Concrete object with parabola-rectangle constitutive law according to Eurocode
    :param conc: Concrete object or fck value
    :param alpha_cc: alpha_cc
    :param gamma_c: gamma_c
    :return:
    """
    f_ck = conc.fck if isinstance(conc, Concrete) else float(conc)
    f_cube = get_cube_EC(f_ck)

    uls_concrete = create_concrete(
        fck=f_ck,
        constitutive_law='parabolarectangle',
        alpha_cc=alpha_cc,
        gamma_c=gamma_c,
        name=f"C{f_ck}/{f_cube} ULS",
    )

    return uls_concrete

def fctm_parabolic_law_EC(concrete: Union[Concrete, float, int], n_c: int = 80, n_t: int = 20) -> CrackingConcreteLawEC:
    """
    Author: Elliot Melcer
    Creates a Non-Linear Constitutive Law with Linear Branch in Tension and Sargin Branch Under Compression
    - Tension: linear elastic (0 → eps_ctm)
    - Compression: Sargin (eps_cu1 → eps_c1)

    Returns a CrackingConcreteLawEC Object
    """

    if not isinstance(concrete, Concrete):
        f_ck = float(concrete)
        _concrete = create_concrete(fck=f_ck, constitutive_law='sargin') #temporary Concrete object, constitutive_law is irrelevant
    else:
        _concrete = concrete

    # -------------------------------
    # Read parameters
    # -------------------------------
    fcm = _concrete.fcm
    Ecm = _concrete.Ecm
    fctm = _concrete.fctm

    eps_c1 = -abs(_concrete.eps_c1)
    eps_cu1 = -abs(_concrete.eps_cu1)
    k = _concrete.k_sargin

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

    return CrackingConcreteLawEC(
        strains=eps,
        stresses=sig,
        eps_cu1=eps_cu1,
        eps_c1 = eps_c1,
        name="CrackingConcreteLawEC",
        flag=0,
    )

def tenstiff_parabolic_law_EC(concrete: Union[Concrete, float, int], n_c: int = 80, n_t: int = 20) -> TensionStiffeningConcreteLawEC:
    """
    Author: Elliot Melcer
    Creates a Non-Linear Constitutive Law
        Compression: Sargin Branch
        Tension:  Linear Branch until fctm + Tension Stiffening according to Naya(2006)

    Returns a TensionStiffeningConcreteLawEC Object
    """

    if not isinstance(concrete, Concrete):
        f_ck = float(concrete)
        _concrete = create_concrete(fck=f_ck, constitutive_law='sargin') #temporary Concrete object, constitutive_law is irrelevant
    else:
        _concrete = concrete

    # -------------------------------
    # Read parameters
    # -------------------------------
    fcm = _concrete.fcm
    Ecm = _concrete.Ecm
    fctm = _concrete.fctm

    eps_c1 = -abs(_concrete.eps_c1)
    eps_cu1 = -abs(_concrete.eps_cu1)
    k = _concrete.k_sargin

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
    eps_t = np.linspace(0.0, eps_ctm, 2, endpoint=True) # dim = 1
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
    # Merge strains and stresses
    # -------------------------------
    eps = np.concatenate((eps_c, eps_t, [eps_P_t], [eps_S_t], [eps_F_t]))
    sig = np.concatenate((sig_c, sig_t, [sig_P_t], [sig_R_t], [0.0]))

    # -------------------------------
    # Final safety check (important)
    # -------------------------------
    eps, unique_idx = np.unique(eps, return_index=True)
    sig = sig[unique_idx]

    return TensionStiffeningConcreteLawEC(
        strains=eps,
        stresses=sig,
        eps_cu1=eps_cu1,
        eps_c1=eps_c1,
        name="TensionStiffeningConcreteLawEC",
        flag=0,
    )

def get_cube_EC(cylinder_strength) -> int:
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


def get_cfrp_reinforcement_from_registry(
        mat_id: str,
        materials: dict,
        prestress_percent: float = 0.0,
        gamma_s: float = 1.3
):
    """
    Create a CFRP-Reinforcement object from materials registry.

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

