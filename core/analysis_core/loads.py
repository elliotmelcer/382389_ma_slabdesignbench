import numpy as np

from slab_construction.slab_construction import SlabConstruction


class Loads:

    """
    Author: Elliot Melcer
    Class for instantiating a load model according to Eurocode 0

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
        EC0 6.10
        """
        Gd = self.gamma_g * (slab_construction.non_structural_dead_load()
                             + slab_construction.non_structural_dead_load())

        Qd = self.gamma_q * float(np.sum(self.Qk * self.psi_0_values))

        return Gd + Qd

    def frequent_combination(self, slab_construction: SlabConstruction):
        """
        Serviceability Limit State (SLS) – frequent combination
        EC0 6.15b
        """
        return (slab_construction.non_structural_dead_load()
                + slab_construction.non_structural_dead_load()
                + float(np.sum(self.Qk * self.psi_1_values)))

    def quasi_permanent_combination(self, slab_construction: SlabConstruction):
        """
        Serviceability Limit State (SLS) – quasi-permanent combination
        EC0 6.16b
        """
        return (slab_construction.non_structural_dead_load()
                + slab_construction.non_structural_dead_load()
                + float(np.sum(self.Qk * self.psi_2_values)))
