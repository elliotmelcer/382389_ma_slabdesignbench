from abc import ABC, abstractmethod

from core.analysis_core.acoustic_methods import calculate_sound_reduction_index, \
    calculate_standard_impact_sound_pressure_level
from slab_construction.slab_construction import SlabConstruction

"""
ACOUSTIC CHECKS
Adapted from Jamila Loutfi and Ahmad Eiz Eddin
"""

class AcousticCheck(ABC):

    @staticmethod
    @abstractmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            limit_dB: float,
            mod_att: float,
            buffer_dB: float = 0.0
    ) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError

"""D.1 Airborne Sound Insulation Check"""

class AirborneSoundInsulationCheck(AcousticCheck):
    @staticmethod
    def calculateUtilization(
        slab_construction: SlabConstruction,
        limit_dB: float,
        mod_att: float,
        buffer_dB: float = 0.0,
        debug_print: bool = False
    ) -> float:
        R_w_min = limit_dB # dB

        R_w = calculate_sound_reduction_index(slab_construction, mod_att = mod_att)
        print("R_w = ", R_w)
        utilization = R_w_min / (R_w - buffer_dB)

        return utilization

"""D.2 Impact Sound Insulation Check"""

class ImpactSoundInsulationCheck(AcousticCheck):
    @staticmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            limit_dB: float,
            mod_att: float,
            buffer_dB: float = 0.0,
            debug_print: bool = False
    ) -> float:
        L_nw_max = limit_dB  # dB

        L_nw = calculate_standard_impact_sound_pressure_level(slab_construction, mod_att=mod_att)
        print("L_nw = ", L_nw)

        utilization = (L_nw + buffer_dB) / L_nw_max

        return utilization
