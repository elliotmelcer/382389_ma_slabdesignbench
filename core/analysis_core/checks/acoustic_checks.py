from abc import ABC, abstractmethod

from core.analysis_core.acoustic_methods import calculate_sound_reduction_index, \
    calculate_standard_impact_sound_pressure_level
from slab_construction.slab_construction import SlabConstruction


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

        utilization = (R_w_min + buffer_dB) / R_w

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

        utilization = L_nw / (L_nw_max - buffer_dB)

        return utilization
