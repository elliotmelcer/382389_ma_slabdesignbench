from contextlib import contextmanager
from pathlib import Path

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from core.analysis_core.checks.acoustic_checks import AirborneSoundInsulationCheck, ImpactSoundInsulationCheck
from core.analysis_core.checks.construction_checks import MidlineConcreteCoverCheck, ReinforcementSpacingCheck, \
    MinimumHPShellThicknessCheck
from core.analysis_core.checks.modeling_checks import NtDyCombinationCheck, BeamTheoryHgesLRatioCheck, \
    BeamTheoryBLRatioCheck
from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE, \
    DeflectionLimitByDeflectionCheckEC2004DE, DeflectionLimitByMcrCheckEC2004DE, \
    FailureAnnouncementByDeflectionCheckEC2004DE, FailureAnnouncementByMcrCheckEC2004DE
from core.analysis_core.statics import SystemType, MomentType
from core.analysis_core.statics.loads import Loads
from core.analysis_core.material_methods import ConcreteCO2Registry, get_material_properties
from core.ioh_core.import_specs import load_materials_registry
from core.unit_core import mm3_to_m3
from slab_construction.slab_construction import SlabConstruction


@contextmanager
def timed(label: str, enabled: bool = True):
    if not enabled:
        yield
        return
    start = time.perf_counter()
    yield
    print(f"Analysis Time {label}: {time.perf_counter() - start:.6f} s")


def analysis(
        slab_construction: SlabConstruction,
        live_loads: Loads,
        defl_sls_case: str = "a",
        n: float = 0.0,
        timed_run: bool = False) -> None:

    _hp_shell = slab_construction.slab.hp_shell

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    materials_csv = PROJECT_ROOT / "slab_construction/slabs/hp_slab/materials.csv"
    materials = load_materials_registry(materials_csv)

    reinf = slab_construction.slab.hp_shell.reinforcement
    reinf_id = reinf.name.split(" prestressed")[0]

    concrete_uls = slab_construction.slab.hp_shell.concrete

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (A) - ULS
    # ======================================================================================================================

    with timed("Check A  ", timed_run):
        m_u_A_util = UltimateMomentCheckEC2004DE.calculate_utilization(
            slab_construction=slab_construction,
            loads=live_loads,
            system=SystemType.SIMPLE_BEAM,
            moment=MomentType.MAX_POS_MOMENT,
            n=n)

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (B) - SLS
    # ======================================================================================================================

    # B.1a Limiting Deflection by Checking the Maximum Deflection against Limit Factor

    with timed("Check B1a", timed_run):
        w_max_B1a_util = DeflectionLimitByDeflectionCheckEC2004DE.calculate_utilization(
            slab_construction=slab_construction,
            loads=live_loads,
            system=SystemType.SIMPLE_BEAM,
            limit_factor=250.
        )

    # B.1b Limiting Deflection by Checking the Quasi-Permanent Moment Against the Cracking Moment

    with timed("Check B1b", timed_run):
        w_max_B1b_util = DeflectionLimitByMcrCheckEC2004DE.calculate_utilization(
            slab_construction=slab_construction,
            loads=live_loads,
            system=SystemType.SIMPLE_BEAM,
            moment=MomentType.MAX_POS_MOMENT,
        )

    # B.2a Check Minimum Deflection under Fundamental Combination

    with timed("Check B2a", timed_run):
        fa_B2a_util = FailureAnnouncementByDeflectionCheckEC2004DE.calculate_utilization(
            slab_construction=slab_construction,
            loads=live_loads,
            system=SystemType.SIMPLE_BEAM,
            min_factor=100.
        )

    # B.2b Limiting Deflection by Checking the Quasi-Permanent Moment Against the Cracking Moment

    with timed("Check B2b", timed_run):
        fa_B2b_util = FailureAnnouncementByMcrCheckEC2004DE.calculate_utilization(
            slab_construction=slab_construction,
            loads=live_loads,
            system=SystemType.SIMPLE_BEAM,
            moment=MomentType.MAX_POS_MOMENT,
        )

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (C) - CONSTRUCTION
    # ======================================================================================================================

    # C.1. Sufficient Concrete Cover from the outermost Reinforcement to the Edge along the HP-Shell Midline

    with timed("Check C1 ", timed_run):
        cc_C1_util = MidlineConcreteCoverCheck.calculate_utilization(
            slab_construction=slab_construction,
        )

    # C.2. Check for Sufficient Clear Spacing between Reinforcement along the HP-Shell Midline

    with timed("Check C2 ", timed_run):
        s_C2_util = ReinforcementSpacingCheck.calculate_utilization(
            slab_construction=slab_construction,
        )

    # C.3 Check for Minimum Shell Thickness

    with timed("Check C3 ", timed_run):
        tmin_C3_util = MinimumHPShellThicknessCheck.calculate_utilization(
            slab_construction=slab_construction,
        )

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (D) - INSULATION
    # ======================================================================================================================

    # D.1 Airborne Sound Insulation Check

    with timed("Check D1 ", timed_run):
        asi_D1_util = AirborneSoundInsulationCheck.calculate_utilization(
            slab_construction=slab_construction,
            limit_dB=54.0,
            mod_att=0.01,
            buffer_dB=2.0
        )

    # D.2 Impact Sound Insulation Check

    with timed("Check D2 ", timed_run):
        isi_D2_util = ImpactSoundInsulationCheck.calculate_utilization(
            slab_construction=slab_construction,
            limit_dB=46.0,
            mod_att=0.01,
            buffer_dB=3.0
        )

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (Z) - MODELING
    # ======================================================================================================================

    # Z.1. Combination of nt and dy

    with timed("Check Z1 ", timed_run):
        ntdy_Z1_util = NtDyCombinationCheck.calculate_utilization(
            slab_construction=slab_construction
        )

    # Z.2. Beam Theory H_ges / L - Ratio

    with timed("Check Z2 ", timed_run):
        beam_hL_Z2_util = BeamTheoryHgesLRatioCheck.calculate_utilization(
            slab_construction=slab_construction,
        )

    # Z.3. Beam Theory B / L - Ratio

    with timed("Check Z3 ", timed_run):
        beam_BL_Z3_util = BeamTheoryBLRatioCheck.calculate_utilization(
            slab_construction=slab_construction,
        )

    # ======================================================================================================================
    # COMPUTE OBJECTIVE FUNCTION
    # ======================================================================================================================

    # Compute Material Quantities
    concrete_m3 = mm3_to_m3(_hp_shell.hp_geometry.volume())
    reinforcement_m3 = mm3_to_m3(_hp_shell.total_reinforcement_volume())

    # Prices in €/m3
    cost_concrete_eur_m3 = ConcreteCO2Registry.cost(concrete_uls)
    cost_reinforcement_eur_m3 = get_material_properties(reinf_id, materials)["cost"]

    # GWP in CO2eq./m3
    gwp_concrete_CO2eq_m3 = ConcreteCO2Registry.gwp(concrete_uls)
    gwp_reinforcement_CO2eq_m3 = get_material_properties(reinf_id, materials)["gwp"]

    # Unpenalized objective function
    y_cost = cost_concrete_eur_m3 * concrete_m3 + cost_reinforcement_eur_m3 * reinforcement_m3
    y_gwp = gwp_concrete_CO2eq_m3 * concrete_m3 + gwp_reinforcement_CO2eq_m3 * reinforcement_m3

    weight_cost = 1.0
    weight_gwp = 1.0

    y = y_cost * weight_cost + y_gwp * weight_gwp

    # ======================================================================================================================
    # COMPUTE PENALIZED OBJECTIVE FUNCTION
    # Adapted from: Max Dombrowski
    # ======================================================================================================================

    constraint_values = {"A_bending_capacity": m_u_A_util}

    if defl_sls_case == "a":
        constraint_values["B1a_deflection_by_wmax_capacity"] = w_max_B1a_util
        constraint_values["B2a_failure_announcement_by_wmin_capacity"] = fa_B2a_util
    else:
        constraint_values["B1b_deflection_by_mcr_capacity"] = w_max_B1b_util
        constraint_values["B2b_failure_announcement_by_mcr_capacity"] = fa_B2b_util

    constraint_values["C1_concrete_cover_capacity"] = cc_C1_util
    constraint_values["C2_clear_spacing_capacity"] = s_C2_util
    constraint_values["C3_shell_thickness_capacity"] = tmin_C3_util
    constraint_values["D1_airborne_sound_insulation_capacity"] = asi_D1_util
    constraint_values["D2_impact_sound_insulation_capacity"] = isi_D2_util
    constraint_values["Z1_nt_dt_combination_capacity"] = ntdy_Z1_util
    constraint_values["Z2_beam_theory_H_L_capacity"] = beam_hL_Z2_util
    constraint_values["Z3_beam_theory_B_L_capacity"] = beam_BL_Z3_util

    print(
        "constraint values: {"
        + ", ".join(f"'{k}': {v:.3f}" for k, v in constraint_values.items())
        + "}"
    )

    penalties_ = {
        name: (1.0 if value <= 1.0 else float(value))
        for name, value in constraint_values.items()
    }

    print(
        "penalties_: {"
        + ", ".join(f"'{k}': {v:.3f}" for k, v in penalties_.items())
        + "}"
    )

    penalty_product_ = 1.0
    for name, v in penalties_.items():
        penalty_product_ *= (v ** 2.0)

    y_p = y * penalty_product_
    print(f"penalty product: {penalty_product_:.3f}")
    print(f"penalized objective function: {y_p:.3f} \n")


if __name__ == "__main__":
    import time

    # print("Analysis: Reference Design")
    # analysis(test_slab_construction_ref, test_loads, timed_run=True)
    # print("")

    # print("C1 Design 1")
    # analysis(test_slab_construction_c1_1, test_loads, timed_run=True)
    # print("")

    # print("C1 Design 2 (C50)")
    # analysis(test_slab_construction_c1_2_c50, test_loads, timed_run=True)
    # print("")

    # print("C1 Design 2 (C80)")
    # analysis(test_slab_construction_c1_2_c80, test_loads, timed_run=True)
    # print("")

    # print("C1 Design 3")
    # analysis(test_slab_construction_c1_3, test_loads, timed_run=True)
    # print("")

    print("C1 Design 4")
    analysis(test_slab_construction_c1_4, test_loads, timed_run=True)
    print("")


