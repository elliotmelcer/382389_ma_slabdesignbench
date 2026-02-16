from abc import ABC, abstractmethod

from structuralcodes.sections import GenericSection

from core.analysis_core.statics.deformations import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces
from core.analysis_core.loads import Loads
from core.analysis_core.section_methods import calculate_bending_strength_uls_Nmm, flipped_section, \
    calculate_cracking_moment_sls_Nmm
from core.unit_core import Nmm_to_kNm
from core.visualization_core.visualization import plot_cross_section
from slab_construction.slab_construction import SlabConstruction


class StructuralCheck(ABC):

    @staticmethod
    @abstractmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str,
            moment: str) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError


class UltimateMomentCheckEC2004DE(StructuralCheck):

    @staticmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str = "SIMPLE_BEAM",
            moment: str = "MAX_POS_MOMENT",
            n: float = 0.0,
            debug_print: bool = False
    ) -> float:
        """
        Calculate utilization ratio for ultimate moment check

        :param debug_print:
        :param n:
        :param slab_construction: Slab construction object
        :param loads: Loads object (only uniformly distributed loads over all spans)
        :param system: Available structural system types:
                            ("CANTILEVER",
                            "SIMPLE_BEAM",
                            "TWO_SPAN",
                            "THREE_SPAN",
                            "FOUR_SPAN" or
                            "FIVE_SPAN")
        :param moment: Moment type
                            ("MAX_POS_MOMENT" or
                            "MAX_NEG_MOMENT")
        :return: Utilization ratio (MEd/MRd)
        """
        slab = slab_construction.slab

        # Normalize string inputs
        system = system.strip().upper()
        moment = moment.strip().upper()

        # Get moment data (coefficient and x-position) from lookup table
        moment_data = InternalForces.get_moment_data(system, moment)
        x_position = moment_data["x_position"]

        # Validate x-position is within bounds for this system
        InternalForces.validate_x_position(system, x_position)

        # Calculate resistance at the specific x-position where max moment occurs
        # x_position is normalized (0 at first support, 1 at second support, etc.)
        if moment == "MAX_POS_MOMENT":
            MRd = -Nmm_to_kNm(
                calculate_bending_strength_uls_Nmm(slab.section_at(x_position), n).get("m_u")
            )
        else:
            rotated_section = flipped_section(slab.section_at(x_position))
            # plot_cross_section(rotated_section)
            MRd = Nmm_to_kNm(
                calculate_bending_strength_uls_Nmm(rotated_section, n).get("m_u")
            )

        # Calculate design moment based on system and moment type
        MEd = InternalForces.calculate_moment(
            slab_construction,
            loads,
            system,
            "FUNDAMENTAL",
            moment_type=moment
        )

        # Calculate utilization
        utilization = abs(MEd / MRd)

        if debug_print:
            print(f"System: {system}, Moment Type: {moment}")
            print(f"x-position: {x_position:.3f}")
            print(f"M_Rd = {MRd:.3f} kNm")
            print(f"M_Ed = {MEd:.3f} kNm")
            print(f"Utilization = {utilization:.3f} ({utilization * 100:.1f}%)\n")

        return utilization

class DeflectionLimitByDeflectionCheckEC2004DE(StructuralCheck):

    @staticmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str = "SIMPLE_BEAM",
            limit_factor: float = 250.0,
            debug: bool = False,
    ) -> float:

        w_max = DeflectionCalculator.calculate_deflection(
            slab_construction,
            loads,
            system,
            combination = "QUASI-PERMANENT",
            debug = debug,
        )

        L = slab_construction.slab.L

        w_limit = L / limit_factor

        utilization = w_max / w_limit

        if debug:
            print("w_max = ", w_max)
            print("L = ", L)

        return utilization

class DeflectionLimitByMcrCheckEC2004DE(StructuralCheck):
    @staticmethod
    def calculateUtilization(
            slab_construction: SlabConstruction,
            loads: Loads,
            system: str = "SIMPLE_BEAM",
            moment: str = "MAX_POS_MOMENT",
            n: float = 0.0,
            debug: bool = False
    ) -> float:
        """
        Calculate the utilization ratio m_qp / m_cr.

        Returns:
            float: Utilization ratio.
                   - < 1.0: Section remains uncracked under quasi-permanent loads
                   - > 1.0: Section will crack
                   - float('inf'): Section crushes before cracking (over-prestressed)
        """

        # Calculate quasi-permanent moment
        m_qp = InternalForces.calculate_moment(
            slab_construction,
            loads,
            system,
            combination = "QUASI-PERMANENT",
            moment_type = moment,
        )

        # Get section at midspan
        section_midspan = slab_construction.slab.section_at(0.5)

        # Calculate cracking moment with physical checks
        m_cr_result = calculate_cracking_moment_sls_Nmm(section_midspan, n)

        # Handle invalid cases (section crushes before cracking)
        if not m_cr_result['valid']:
            return float('inf')

        # Get cracking moment magnitude
        m_cr = abs(Nmm_to_kNm(m_cr_result["m_cr"]))

        # Avoid division by zero (shouldn't happen with valid result, but safety check)
        if m_cr < 1e-6:
            return float('inf')

        # Calculate utilization (compare magnitudes)
        utilization = abs(m_qp) / m_cr

        if debug:
            print(f"m_qp = {m_qp:.3f} kNm")

            print(f"m_cr valid: {m_cr_result['valid']}")
            if not m_cr_result['valid']:
                print(f"  Reason: {m_cr_result['reason']}")

            print(f"m_cr = {m_cr:.3f} kNm")

            print(f"utilization = |{m_qp:.3f}| / {m_cr:.3f} = {utilization:.3f}")

        return utilization