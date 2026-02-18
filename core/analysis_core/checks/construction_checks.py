"""CONSTRUCTION REQUIREMENTS"""
from abc import ABC, abstractmethod

import numpy as np

from slab_construction.slab_construction import SlabConstruction



class ConstructionCheck(ABC):

    @staticmethod
    @abstractmethod
    def calculateUtilization(
            slab_construction: SlabConstruction) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError


"""C.1. Check for Sufficient Concrete Cover from the outer most Reinforcement to the Edge along the HP-Shell Midline """

class MidlineConcreteCoverCheck(ConstructionCheck):
    @staticmethod
    def calculateUtilization(
            slab_construction: SlabConstruction
    ) -> float:
        # get geometry
        hp_shell = slab_construction.slab.hp_shell

        # required clear concrete cover
        d_p_mm = hp_shell.d_p()
        c_nom_req = 3 * d_p_mm

        # available clear concrete cover
        c_nom = hp_shell.c_1_clear_concrete_cover()

        utilization = c_nom_req / c_nom

        return utilization