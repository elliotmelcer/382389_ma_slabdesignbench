import numpy as np
from unicodedata import category

from slab_construction.slab_construction import SlabConstruction


class Loads:

    """
    Author: Elliot Melcer
    Class for instantiating a load object based on Eurocode 0 and 1

    Note: only uniformly distributed loads over ALL spans
    """

    def __init__(
        self,
        live_loads,
        psi_0_values,
        psi_1_values,
        psi_2_values,
        gamma_g = 1.35,
        gamma_q = 1.5,
    ):
        self.Qk = np.array(live_loads, dtype=float)
        self.psi_0_values = np.array(psi_0_values, dtype=float)
        self.psi_1_values = np.array(psi_1_values, dtype=float)
        self.psi_2_values = np.array(psi_2_values, dtype=float)
        self.gamma_g = gamma_g
        self.gamma_q = gamma_q
        self._check_dimensions()

    # Format: "psi": (psi_0, psi_1, psi_2)
    # Qk in kN/m²
    PSI_TABLE_EC_2004_DE = {
        "A": {"psi": (0.7, 0.5, 0.3), "Qk": {1: 1.0, 2: 1.5, 3: 2.0}},
        "B": {"psi": (0.7, 0.5, 0.3), "Qk": {1: 2.0, 2: 3.0, 3: 5.0}},
        "C": {"psi": (0.7, 0.7, 0.6), "Qk": {1: 3.0, 2: 4.0, 3: 5.0, 4: 5.0, 5: 5.0, 6: 7.5}},
        "D": {"psi": (0.7, 0.7, 0.6), "Qk": {1: 2.0, 2: 5.0, 3: 5.0}},
        "E": {"psi": (1.0, 0.9, 0.8), "Qk": {1: 5.0, 2: 6.0, 3: 7.5}},
    }

    @classmethod
    def _parse_category(cls, _category: str):
        """
        Translates a given category into the corresponding Load and combination values from the PSI_TABLE
        :param _category:
        :return:
        """
        key = _category.upper().strip()
        letter, number = key[0], int(key[1:])
        if letter not in cls.PSI_TABLE_EC_2004_DE:
            raise ValueError(f"Unknown category '{letter}'")
        if number not in cls.PSI_TABLE_EC_2004_DE[letter]["Qk"]:
            raise ValueError(f"Unknown subcategory '{number}' for category '{letter}'")
        psi = cls.PSI_TABLE_EC_2004_DE[letter]["psi"]
        Qk = cls.PSI_TABLE_EC_2004_DE[letter]["Qk"][number]
        return Qk, psi[0], psi[1], psi[2]

    @classmethod
    def from_categories(cls, categories: str | list[str], gamma_g=1.35, gamma_q=1.5):
        # Normalize Input
        if isinstance(categories, str):
            categories = [categories]

        Qk_values, psi_0s, psi_1s, psi_2s = [], [], [], []

        for cat in categories:
            Qk, psi_0, psi_1, psi_2 = cls._parse_category(cat)
            Qk_values.append(Qk)
            psi_0s.append(psi_0)
            psi_1s.append(psi_1)
            psi_2s.append(psi_2)

        return cls(Qk_values, psi_0s, psi_1s, psi_2s, gamma_g, gamma_q)

    def _check_dimensions(self) -> None:
        """
        Checks the dimension compatibility of the input.
        """
        n = len(self.Qk)
        for arr in [self.psi_0_values, self.psi_1_values, self.psi_2_values]:
            if len(arr) != n:
                raise ValueError("All live load (Qk) and psi arrays must have the same length")

    def fundamental_combination(self, slab_construction: SlabConstruction):
        """
        Ultimate Limit State (ULS) - fundamental combination
        EC0 6.10: Σ(j≥1) γ_G,j*G_k,j "+" γ_p*P "+" γ_Q,1*Q_k,1 "+" Σ(i>1) γ_Q,i*ψ_0,i*Q_k,i
        """
        Gd = self.gamma_g * (slab_construction.structural_dead_load()
                             + slab_construction.non_structural_dead_load())

        # Only the accompanying actions are multiplied by psi_0
        psi_0_mask = self.psi_0_values.copy()
        psi_0_mask[0] = 1.0

        Qd = self.gamma_q * float(np.sum(self.Qk * psi_0_mask))

        return Gd + Qd

    def frequent_combination(self, slab_construction: SlabConstruction):
        """
        Serviceability Limit State (SLS) – frequent combination
        EC0 6.15b: Σ(j≥1) G_k,j "+" P "+" ψ_1,1*Q_k,1 "+" Σ(i>1) ψ_2,i*Q_k,i
        """

        # set up psi values for frequent combination
        psi_mask = self.psi_2_values.copy()
        psi_mask[0] = self.psi_1_values[0]

        return (slab_construction.structural_dead_load()
                + slab_construction.non_structural_dead_load()
                + float(np.sum(self.Qk * self.psi_1_values)))

    def quasi_permanent_combination(self, slab_construction: SlabConstruction):
        """
        Serviceability Limit State (SLS) – quasi-permanent combination
        EC0 6.16b: Σ(j≥1) G_k,j "+" P "+" Σ(i≥1) ψ_2,i*Q_k,i
        """
        return (slab_construction.structural_dead_load()
                + slab_construction.non_structural_dead_load()
                + float(np.sum(self.Qk * self.psi_2_values)))