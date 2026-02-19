from abc import ABC, abstractmethod

from slab_construction.slab_construction import SlabConstruction


class ModelingCheck(ABC):

    @staticmethod
    @abstractmethod
    def calculateUtilization(
            slab_construction: SlabConstruction) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError


"""Z.1. Combination of nt and dy """

class NtDyCombinationCheck(ModelingCheck):
    @staticmethod
    def calculateUtilization(slab_construction: SlabConstruction) -> float:
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