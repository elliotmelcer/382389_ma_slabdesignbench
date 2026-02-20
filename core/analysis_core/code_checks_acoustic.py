from slab_construction.slab_construction import SlabConstruction, InfillMaterial


def calculate_sound_reduction_index(slab_construction: SlabConstruction, _mod_att: float) -> float:
    """
    Author: Jamila Loutfi
    Calculate sound reduction index for a slab construction.
    Note: Only considers DIRECT sound reduction index
    """

    hp_geometry = slab_construction.slab.hp_shell.hp_geometry
    floor = slab_construction.floor

    _B = hp_geometry.B
    _t = hp_geometry.t
    _t_infill = floor.get_layer_by_type(InfillMaterial)

    regression_R = 41.61 + 727.32 * _mod_att + 53.55 * _t_infill + 1.51 * _B - 11.52 * _B * _t

    return 0.0