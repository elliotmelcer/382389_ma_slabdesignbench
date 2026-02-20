import math

from slab_construction.floor import InfillMaterial, InsulationMaterial, ScreedMaterial
from slab_construction.slab_construction import SlabConstruction


def calculate_sound_reduction_index(
        slab_construction: SlabConstruction,
        mod_att: float,
        debug: bool = False
) -> float:
    """
    Author: Jamila Loutfi
    Calculate sound reduction index for a slab construction.
    Note: Only considers DIRECT sound reduction index
    """

    hp_geometry = slab_construction.slab.hp_shell.hp_geometry
    floor = slab_construction.floor

    _B = hp_geometry.B / 1000 # [m]
    _t = hp_geometry.t / 1000 # [m]
    _t_infill = floor.get_layer_by_type(InfillMaterial).thickness / 1000 # [m]

    # Regression Model
    regression_Rw = 41.61 + 727.32 * mod_att + 53.55 * _t_infill + 1.51 * _B - 11.52 * _B * _t

    insulation_layer = floor.get_layer_by_type(InsulationMaterial)
    _E_dyn = insulation_layer.material.E_dyn / insulation_layer.thickness * 1000 # MN/m³

    "unclear how m_concrete_slab should be calculated"
    m_concrete_slab = slab_construction.slab.self_load() * 1000 / 10  # kg/m²
    # m_concrete_slab = 2400 * _t  # kg/m²

    m_infill = slab_construction.infill_area_density_kg_m2()                   #kg/m²
    m_screed = floor.get_layer_by_type(ScreedMaterial).area_density_kg_m2()    #kg/m²

    m1 = m_infill + m_concrete_slab
    m2 = m_screed

    # Resonant Frequency f0 according to DIN 4109-34 Eq. (1)
    resonant_frequency_f0 = 160 * (_E_dyn * (1/m1 + 1/m2) ) ** 0.5

    # Improvement of the Sound Reduction Index according to nach DIN 4109-34 Table 1
    delta_R = (74.4 - 20 * math.log10(resonant_frequency_f0)) - (regression_Rw / 2)

    sound_reduction_index_R_w = regression_Rw + delta_R

    if debug:
        print(f"R_w,BG = {regression_Rw:.2f} \n")

        print(f"_E_dyn = {_E_dyn:.2f}")
        print(f"m_concrete_slab = {m_concrete_slab:.2f}")
        print(f"m_infill = {m_infill:.2f}")
        print(f"m_screed = {m_screed:.2f}")
        print(f"Resonant Frequency F0 = {resonant_frequency_f0:.2f}")

        print(f"delta_R = {delta_R:.2f}")

    return sound_reduction_index_R_w