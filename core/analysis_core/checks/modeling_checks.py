from abc import ABC, abstractmethod

from slab_construction.slab_construction import SlabConstruction

"""
MODELING CHECKS
Adapted from Jamila Loutfi
"""

class ModelingCheck(ABC):
    """
    Author: Elliot Melcer
    Abstract class for modeling checks
    """
    @staticmethod
    @abstractmethod
    def calculate_utilization(
            slab_construction: SlabConstruction
    ) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError


"""Z.1. Combination of nt and dy """

class NtDyCombinationCheck(ModelingCheck):
    @staticmethod
    def calculate_utilization(slab_construction: SlabConstruction) -> float:
        # get geometry
        hp_geometry = slab_construction.slab.hp_shell.hp_geometry

        nt = hp_geometry.nt
        dy = hp_geometry.dy
        dy_real = hp_geometry.dy_real()

        if nt == 1:
            if abs(dy - dy_real) > 0.01:
                utilization = 10.0
            else:
                utilization = 1.0
        else:
            utilization = 1.0

        return utilization


"""Z.2. Beam Theory H_ges / L - Ratio """

class BeamTheoryHgesLRatioCheck(ModelingCheck):
    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            f_b: float = 5.0
    ) -> float:
        # get geometry
        hp_geometry = slab_construction.slab.hp_shell.hp_geometry

        Hx = hp_geometry.Hx
        Hy = hp_geometry.Hy
        L = hp_geometry.L

        utilization = (Hx + Hy) / (L / f_b)

        return utilization

"""Z.3. Beam Theory B / L - Ratio """

class BeamTheoryBLRatioCheck(ModelingCheck):
    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            f_b: float = 5.0
    ) -> float:
        # get geometry
        hp_geometry = slab_construction.slab.hp_shell.hp_geometry

        L = hp_geometry.L
        B = hp_geometry.B

        utilization = B / (L / f_b)

        return utilization