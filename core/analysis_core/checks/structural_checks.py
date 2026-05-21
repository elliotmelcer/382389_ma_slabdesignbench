from abc import ABC, abstractmethod

from core.analysis_core.statics.constants import SystemType, MomentType
from core.analysis_core.statics.new_deflection import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces
from core.analysis_core.statics.loads import LoadsEC
from core.analysis_core.section_methods import calculate_bending_strength_uls_Nmm, flipped_section, \
    calculate_cracking_moment_sls_Nmm
from core.unit_core import Nmm_to_kNm
from slab_construction.slab_construction import SlabConstruction

"""
STRUCTURAL CHECKS
A.1, B.1a, B.1b, B.2a, B.2b adapted from Jamila Loutfi
"""

class StructuralCheck(ABC):
    """
    Author: Elliot Melcer
    Abstract class for structural checks
    """
    @staticmethod
    @abstractmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: str,
            moment: str) -> float:
        """Returns the utilization ratio"""
        raise NotImplementedError

"""ULTIMATE LIMIT STATE"""

"""A.1 Ultimate Moment Check"""
class UltimateMomentCheckEC2004DE(StructuralCheck):

    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: SystemType = SystemType.SIMPLE_BEAM,
            moment: MomentType = MomentType.MAX_POS_MOMENT,
            n: float = 0.0,
            debug_print: bool = False
    ) -> float:
        """
        Calculate utilization ratio for ultimate moment check

        :param debug_print:
        :param n:
        :param slab_construction: Slab construction object
        :param loads: LoadsEC object (only uniformly distributed loads over all spans)
        :param system: System type (see Enum)
        :param moment: Moment type (see Enum)
        :return: Utilization ratio (MEd/MRd)
        """
        slab = slab_construction.slab

        # Get moment data (coefficient and x-position) from lookup table
        moment_data = InternalForces.get_moment_data(system, moment)
        x_position = moment_data["x_position"]

        # Validate x-position is within bounds for this system
        InternalForces.validate_x_position(system, x_position)

        # Calculate resistance at the specific x-position where max moment occurs
        # x_position is normalized (0 at first support, 1 at second support, etc.)
        if moment == MomentType.MAX_POS_MOMENT:
            MRd_kNm = -Nmm_to_kNm(
                calculate_bending_strength_uls_Nmm(slab.section_at(x_position), n).get("m_u")
            )
        else:
            rotated_section = flipped_section(slab.section_at(x_position))
            # plot_cross_section(rotated_section)
            MRd_kNm = Nmm_to_kNm(
                calculate_bending_strength_uls_Nmm(rotated_section, n).get("m_u")
            )

        # Calculate design moment based on system and moment type
        MEd_kNm = InternalForces.calculate_moment_kNm(
            slab_construction,
            loads,
            system,
            combination="FUNDAMENTAL",
            moment=moment
        )

        # Calculate utilization
        utilization = abs(MEd_kNm / MRd_kNm)

        if debug_print:
            print(f"System: {system}, Moment Type: {moment}")
            print(f"x-position: {x_position:.3f}")
            print(f"M_Rd = {MRd_kNm:.3f} kNm")
            print(f"M_Ed = {MEd_kNm:.3f} kNm")
            print(f"Utilization = {utilization:.3f} ({utilization * 100:.1f}%)\n")

        return utilization


"""SERVICEABILITY LIMIT STATE"""

"""B.1a Deflection Limit Check"""
class DeflectionLimitByDeflectionCheckEC2004DE(StructuralCheck):

    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: SystemType = SystemType.SIMPLE_BEAM,
            limit_factor: float = 250.0,
            debug: bool = False,
    ) -> float:

        w_max_sls = DeflectionCalculator.calculate_deflection_mm(
            slab_construction,
            loads,
            system,
            combination = "QUASI-PERMANENT",
            debug = debug,
        )

        L = slab_construction.slab.L

        w_limit = L / limit_factor

        utilization = w_max_sls / w_limit

        if utilization < 0:
            # Negative deformation is undesirable
            screened_utilization = 1 + abs(utilization)
        else:
            screened_utilization = utilization

        if debug:
            print("raw util = ", utilization)
            print("w_max = ", w_max_sls)
            print("L = ", L)

        return screened_utilization

"""B.1b Deflection Limit Check"""
class DeflectionLimitByMcrCheckEC2004DE(StructuralCheck):
    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: SystemType = SystemType.SIMPLE_BEAM,
            moment: MomentType = MomentType.MAX_POS_MOMENT,
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
        m_qp_kNm = InternalForces.calculate_moment_kNm(
            slab_construction,
            loads,
            system,
            combination = "QUASI-PERMANENT",
            moment = moment,
        )

        # Get section at midspan
        section_midspan = slab_construction.slab.section_at(0.5)

        # Calculate cracking moment with physical checks
        m_cr_result = calculate_cracking_moment_sls_Nmm(section_midspan, n)

        # Handle invalid cases (section crushes before cracking)
        if not m_cr_result['valid']:
            return 99.

        # Get cracking moment magnitude
        m_cr = abs(Nmm_to_kNm(m_cr_result["m_cr"]))

        # Avoid division by zero (shouldn't happen with valid result, but safety check)
        if m_cr < 1e-6:
            return 99.

        # Calculate utilization (compare magnitudes)
        utilization = abs(m_qp_kNm) / m_cr

        if debug:
            print(f"m_qp = {m_qp_kNm:.3f} kNm")

            print(f"m_cr valid: {m_cr_result['valid']}")
            if not m_cr_result['valid']:
                print(f"  Reason: {m_cr_result['reason']}")

            print(f"m_cr = {m_cr:.3f} kNm")

            print(f"utilization = |{m_qp_kNm:.3f}| / {m_cr:.3f} = {utilization:.3f}")

        return utilization

"""B.2a Failure Announcement"""
class FailureAnnouncementByDeflectionCheckEC2004DE(StructuralCheck):
    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: SystemType = SystemType.SIMPLE_BEAM,
            min_factor: float = 250.0,
            debug: bool = False,
    ) -> float:

        w_max_uls = DeflectionCalculator.calculate_deflection_mm(
            slab_construction,
            loads,
            system,
            combination="FUNDAMENTAL",
            debug=debug,
        )

        L = slab_construction.slab.L

        w_min = L / min_factor


        utilization = w_min / w_max_uls

        if utilization < 0:
            # Negative deformation is undesirable
            screened_utilization = 1 + abs(utilization)
        else:
            screened_utilization = utilization

        if debug:
            print(f"w_max = {w_max_uls:.2f}")
            print(f"w_min = {w_min:.2f}")
            print(f"util raw = {w_min:.2f} / {w_max_uls:.2f} = {utilization:.2f}")
            print(f"util = {screened_utilization:.2f}")

        return screened_utilization

"""B.2b Failure Announcement"""
class FailureAnnouncementByMcrCheckEC2004DE(StructuralCheck):
    @staticmethod
    def calculate_utilization(
            slab_construction: SlabConstruction,
            loads: LoadsEC,
            system: SystemType = SystemType.SIMPLE_BEAM,
            moment: MomentType = MomentType.MAX_POS_MOMENT,
            n: float = 0.0,
            debug: bool = False
    ) -> float:
        """
        Calculate the utilization ratio m_qp / m_cr.

        Returns:
            float: Utilization ratio.
                   - < 1.0 : Section remains uncracked under quasi-permanent loads
                   - > 1.0 : Section will crack
                   - 99.0  : Section crushes before cracking (over-prestressed)
        """

        # Calculate fundamental combination moment
        m_fund_kNm = InternalForces.calculate_moment_kNm(
            slab_construction,
            loads,
            system,
            combination = "FUNDAMENTAL",
            moment = moment,
        )

        # Get section at midspan
        section_midspan = slab_construction.slab.section_at(0.5)

        # Calculate cracking moment with physical checks
        m_cr_result = calculate_cracking_moment_sls_Nmm(section_midspan, n)

        # Handle invalid cases (section crushes before cracking)
        if not m_cr_result['valid']:
            return 99.

        # Get cracking moment magnitude
        m_cr = abs(Nmm_to_kNm(m_cr_result["m_cr"]))

        # Avoid division by zero (shouldn't happen with valid result, but safety check)
        if m_cr < 1e-6:
            return 99.

        # Calculate utilization (compare magnitudes)
        utilization = m_cr / m_fund_kNm

        if debug:
            print(f"m_fund = {m_fund_kNm:.3f} kNm")

            print(f"m_cr valid: {m_cr_result['valid']}")
            if not m_cr_result['valid']:
                print(f"  Reason: {m_cr_result['reason']}")

            print(f"m_cr = {m_cr:.3f} kNm")

            print(f"utilization = {m_cr:.3f}/ {m_fund_kNm:.3f} = {utilization:.3f}")

        return utilization