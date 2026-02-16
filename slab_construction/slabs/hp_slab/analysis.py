"""
Perform all Checks here
"""
from structuralcodes import set_design_code
from structuralcodes.materials.concrete import create_concrete

from core.analysis_core.checks.structural_checks import UltimateMomentCheckEC2004DE, \
    DeflectionLimitByDeflectionCheckEC2004DE, DeflectionLimitByMcrCheckEC2004DE
from core.analysis_core.loads import Loads
from core.analysis_core.material_methods import get_cube, get_reinforcement_from_registry, \
    get_floor_material_from_registry, ConcreteCO2Registry, get_material_properties
from core.ioh_core.io_util import _req_param
from core.unit_core import mm3_to_m3
from core.visualization_core.visualization import plot_cross_section
from slab_construction.slab_construction import FloorLayer, Floor, SlabConstruction
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab


def analysis(params: dict, constraints: dict, materials: dict, debug: bool = False) -> dict:
    """
        Return all results -> unpenalized-objective + penalized-objective + all constraints (weight = exponent = 1)so we compute it ONCE.
        """
    #  analysis(params)(slab - specific) computes everything:
    # - unpenalized objective y,
    # - penalized objective y_p (apply weights / exponents / logic internally)
    # - raw violations per constraint in result["violations"][ < name >]
    # - default we set enforcement=HIDDEN, weight=1, exponent=1 (users can still override in runs.csv, but it’s not needed).
    # - the IOH-problem can get all these infos from the cache

    # ======================================================
    # EXTRACT PARAMETERS
    # ======================================================

    # Geometry
    span_mm     = _req_param(params, "geom_span_mm")
    B_mm        = _req_param(params, "geom_b_mm")
    h_ges_mm    = _req_param(params, "geom_h_ges_mm")
    t_mm        = _req_param(params, "geom_t_mm")
    nt          = int(_req_param(params, "geom_nt"))
    dy_mm       = _req_param(params, "geom_dy_mm")
    hx_hges_ratio = _req_param(params, "geom_hx_hges_ratio")

    # Concrete
    conc_fck_MPa = _req_param(params, "mat_conc_fck")

    # Reinforcement
    reinf_id = params.get("mat_reinf_id", "")

    reinf_area_mm2 = _req_param(params, "reinf_a_tex_mm2")
    prestress_pct = _req_param(params, "reinf_kap_t_percent")

    # Floor Materials
    infill_id = params.get("mat_infill_id", "")
    insu_id = params.get("mat_insu_id", "")
    screed_id = params.get("mat_screed_id", "")

    infill_t_mm = _req_param(params, "geom_t_infill_mm")
    insu_t_mm = _req_param(params, "geom_t_insulation_mm")
    screed_t_mm = _req_param(params, "geom_t_screed_mm")

    # Loads

    n = _req_param(params,"loads_N_kN")
    q = _req_param(params,"loads_q_kNm2")

    # Deformations

    defl_limit_factor_w_max = _req_param(params, "defl_max_defl_limit")
    defl_limit_factor_announce_failure = _req_param(params, "defl_max_announce_failure")

    # ======================================================================================================================
    # CREATE MATERIALS
    # ======================================================================================================================
    set_design_code('ec2_2004')

    # Concrete

    concrete_uls = create_concrete(
        fck=conc_fck_MPa,
        constitutive_law ='parabolarectangle',
        alpha_cc = 0.85,
        gamma_c = 1.5,
        name = f"C {conc_fck_MPa}/{get_cube(conc_fck_MPa)} ULS")

    # Reinforcement
    try:
        reinforcement = get_reinforcement_from_registry(
            mat_id=reinf_id,
            materials=materials,
            prestress_percent=prestress_pct,
            gamma_s=1.3
        )
    except (KeyError, ValueError) as e:
        print(f"Error creating reinforcement: {e}")
        # Return infeasible solution
        return {
            "y": float("inf"),
            "y_p": float("inf"),
            "violations": {"material_error": 1.0},
            "params": params
        }

    # Floor materials
    try:
        infill_material = get_floor_material_from_registry(infill_id, materials)
        insulation_material = get_floor_material_from_registry(insu_id, materials)
        screed_material = get_floor_material_from_registry(screed_id, materials)
    except (KeyError, ValueError) as e:
        print(f"Error creating floor materials: {e}")
        return {
            "y": float("inf"),
            "y_p": float("inf"),
            "violations": {"material_error": 1.0},
            "params": params
        }

    # ======================================================================================================================
    # CREATE FLOOR
    # ======================================================================================================================

    infill_layer            = FloorLayer(infill_material, infill_t_mm)
    sound_insulation_layer  = FloorLayer(insulation_material, insu_t_mm)
    screed_layer            = FloorLayer(screed_material, screed_t_mm)

    floor = Floor([infill_layer, sound_insulation_layer, screed_layer])

    # ======================================================================================================================
    # CREATE HP SLAB
    # ======================================================================================================================

    # Calculate Hx and Hy
    Hx_mm = hx_hges_ratio       * h_ges_mm
    Hy_mm = (1-hx_hges_ratio)   * h_ges_mm

    # HP Geometry
    hp_geom = HPGeometry(
        B=B_mm,
        L=span_mm,
        Hx=Hx_mm,
        Hy=Hy_mm,
        t=t_mm,
        dy=dy_mm,
        nt=nt
    )

    # HP-Shell
    hp_shell = HPShell(hp_geom, concrete_uls, reinforcement, reinf_area = reinf_area_mm2)

    # HP-Slab
    hp_slab = HPSlab(hp_shell, infill_material)

    # HP-Slab Construction
    slab_construction = SlabConstruction(hp_slab, floor)


    # ======================================================================================================================
    # LIVE LOADS
    # ======================================================================================================================

    live_loads = Loads([q], [1.0], [1.0], [0.3])

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (A) - ULS
    # ======================================================================================================================

    m_u_util = UltimateMomentCheckEC2004DE.calculateUtilization(
        slab_construction = slab_construction,
        loads = live_loads,
        system = "SIMPLE_BEAM",
        moment = "MAX_POS_MOMENT",
        n = n)

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (B) - SLS
    # ======================================================================================================================

    # B.1a Limiting Deflection by Checking the Maximum Deflection against Limit Factor

    w_max_sls_util = DeflectionLimitByDeflectionCheckEC2004DE.calculateUtilization(
        slab_construction = slab_construction,
        loads = live_loads,
        system = "SIMPLE_BEAM",
        limit_factor=defl_limit_factor_w_max
    )

    # B.1b Limiting Deflection by Checking the Quasi-Permanent Moment Against the Cracking Moment

    w_max_uls_util = DeflectionLimitByMcrCheckEC2004DE.calculateUtilization(
        slab_construction = slab_construction,
        loads = live_loads,
        system = "SIMPLE_BEAM",
        moment = "MAX_POS_MOMENT",
    )

    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (C) - CONSTRUCTION
    # ======================================================================================================================


    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (D) - INSULATION
    # ======================================================================================================================


    # ======================================================================================================================
    # COMPUTE CONSTRAINTS (Z) - MODELING
    # ======================================================================================================================


    # ======================================================================================================================
    # COMPUTE OBJECTIVE FUNCTION
    # ======================================================================================================================

    # Compute Material Quantities
    concrete_m3 = mm3_to_m3(hp_shell.hp_geometry.volume())
    reinforcement_m3 = mm3_to_m3(hp_shell.total_reinforcement_volume())
    # infill_m3 = mm3_to_m3(hp_slab.minimum_infill_volume())

    # Prices in €/m3
    cost_concrete_eur_m3 = ConcreteCO2Registry.cost(concrete_uls)
    cost_reinforcement_eur_m3 = get_material_properties(reinf_id, materials)["cost"]

    # GWP in CO2eq./m3
    gwp_concrete_CO2eq_m3 = ConcreteCO2Registry.gwp(concrete_uls)
    gwp_reinforcement_CO2eq_m3 = get_material_properties(reinf_id, materials)["gwp"]

    # Unpenalized objective function
    y_cost = cost_concrete_eur_m3 * concrete_m3 + cost_reinforcement_eur_m3 * reinforcement_m3
    y_gwp = gwp_concrete_CO2eq_m3 * concrete_m3 + gwp_reinforcement_CO2eq_m3 * reinforcement_m3

    weight_cost = _req_param(params, "weight_omega_2_cost")
    weight_gwp = _req_param(params, "weight_omega_1_gwp")

    y = y_cost * weight_cost + y_gwp * weight_gwp

    # ======================================================================================================================
    # COMPUTE PENALIZED OBJECTIVE FUNCTION
    # Author: Max Dombrowski
    # ======================================================================================================================
    # Collect constraint values
    constraint_values = {  # utilisation ratios
        f"bending_capacity": m_u_util,
        f"deflection_by_wmax_capacity": w_max_sls_util,
        f"deflection_by_mcr_capacity": w_max_uls_util,
    }

    print(
        "constraint values: {"
        + ", ".join(f"'{k}': {v:.3f}" for k, v in constraint_values.items())
        + "}"
    )

    # penalty factors: 1 if satisfied, utilisation value if > 1
    penalties_ = {
        name: (1.0 if value <= 1.0 else float(value))
        for name, value in constraint_values.items()
    }

    print(
        "penalties_: {"
        + ", ".join(f"'{k}': {v:.3f}" for k, v in penalties_.items())
        + "}"
    )

    # compile a list of constraints that are active for this problem to return them
    active_penalties_ = {
        name: penalties_[name]
        for name, meta in constraints.items()
        if meta.get("active", True) and name in penalties_
    }

    # Multiplicative penalty: product of (penalty^2)
    penalty_product_ = 1.0
    for name, v in active_penalties_.items():
        # v >= 1 by construction
        penalty_product_ *= (v ** 2.0)

    y_p = y * penalty_product_
    print(f"penalty product: {penalty_product_:.3f}")
    print(f"penalized objective function: {y_p:.3f} \n")

    if debug:
        # After calculating constraints
        print(f"\nDEBUG constraint_values:")
        for k, v in constraint_values.items():
            print(f"  {k}: {v} (type: {type(v).__name__}, is_inf: {v == float('inf')})")

        print(f"\nDEBUG penalties_:")
        for k, v in penalties_.items():
            print(f"  {k}: {v} (type: {type(v).__name__})")

        print(f"\nDEBUG penalty_product_: {penalty_product_} (type: {type(penalty_product_).__name__})")
    # ======================================================================================================================
    # PLOT CROSS-SECTION
    # ======================================================================================================================


    # ======================================================================================================================
    # RETURN RESULTS
    # ======================================================================================================================

    return {
        "y": y,
        "y_p": y_p,
        "constraint_values": constraint_values,
        "penalties_": active_penalties_,
        "params": dict(params),
        "feasible": True,
        "analysis_error": None,
    }

