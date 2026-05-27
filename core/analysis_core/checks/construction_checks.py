
from abc import ABC, abstractmethod

import numpy as np

from slab_construction.slab_construction import SlabConstruction

"""
CONSTRUCTION CHECKS
Adapted from Jamila Loutfi
"""

class ConstructionCheck(ABC):
    """
    Author: Elliot Melcer
    Abstract class for construction checks
    """
    @staticmethod
    @abstractmethod
    def calculate_utilization(
            slab_construction: SlabConstruction) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError


"""C.1. Check for Sufficient Concrete Cover from the outermost Reinforcement to the Edge along the HP-Shell Midline """

class MidlineConcreteCoverCheck(ConstructionCheck):
    @staticmethod
    def calculate_utilization(slab_construction: SlabConstruction) -> float:
        # get geometry
        hp_shell = slab_construction.slab.hp_shell

        # required clear concrete cover
        d_p_mm = hp_shell.d_p()
        c_nom_c1_req = 3 * d_p_mm

        # available clear concrete cover
        c_nom_c1 = hp_shell.c_1_clear_concrete_cover()

        utilization = c_nom_c1_req / c_nom_c1

        return utilization

"""C.2. Check for Sufficient Clear Spacing between Reinforcement along the HP-Shell Midline """

class ReinforcementSpacingCheck(ConstructionCheck):
    @staticmethod
    def calculate_utilization(slab_construction: SlabConstruction, debug_print: bool = False) -> float:
        # get geometry
        hp_shell = slab_construction.slab.hp_shell

        # required reinforcement spacing
        d_p_mm = hp_shell.d_p()
        s_req = 5.75 * d_p_mm

        # minimum available clear spacing
        s_min = hp_shell.s_min_clear_reinf_spacing()

        if debug_print:
            print(f"s_min = {s_min}")

        if s_min == 0:
            return 10.
        else:
            utilization = s_req / s_min

        return utilization

"""C.3. Check for Minimum Shell Thickness """

class MinimumHPShellThicknessCheck(ConstructionCheck):
    @staticmethod
    def calculate_utilization(slab_construction: SlabConstruction) -> float:
        # get geometry
        hp_shell = slab_construction.slab.hp_shell

        # required clear concrete cover
        d_p_mm = hp_shell.d_p()

        # C.1 an C.2 requirements
        c_nom_c1_req = 3 * d_p_mm
        s_c2_req = 5.75 * d_p_mm

        # shell thickness
        t_req = 2 * d_p_mm + 2 * c_nom_c1_req + s_c2_req

        # available clear concrete cover
        t = hp_shell.hp_geometry.t

        utilization = t_req / t

        return utilization