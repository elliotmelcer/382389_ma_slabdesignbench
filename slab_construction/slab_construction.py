from dataclasses import dataclass

from structuralcodes.core.base import Material
from slab_construction.slabs.slab import Slab



@dataclass(slots=True)
class FloorLayer:
    """
    Author: Elliot Melcer
    Basic Class to model floor layers
    Note: Thickness in [mm] to keep in line with all other dimensions in structuralcodes
    """
    material: Material
    thickness: float

class FloorMaterial(Material):
    """
    Author: Elliot Melcer
    Instantiable Simple Material for floor layers.
    """
    def __init__(self, density: float, name: str | None = "FloorMaterial") -> None:
        super().__init__(density=density, name=name)

class Floor:
    """
    Author: Elliot Melcer
    Class to model a floor construction made up of floor layers
    """
    def __init__(self, layers: list[FloorLayer] | None = None) -> None:
        self.layers: list[FloorLayer] = list(layers) if layers is not None else []

    def add_layer(self, material: Material, thickness: float) -> None:
        """
        Adds a layer
        Note: Thickness in [mm] to keep in line with all other dimensions in structuralcodes
        """
        if thickness <= 0:
            raise ValueError("Thickness must be positive")

        self.layers.append(FloorLayer(material, thickness))

    def dead_load(self) -> float:
        """
        Calculates the total dead load of the floor layers [kN/m²].
        """
        floor_dead_load = sum(
            layer.material.density * layer.thickness * 1e-5
            for layer in self.layers
        )

        return floor_dead_load

class SlabConstruction:
    """
    Author: Elliot Melcer
    Class to model a complete slab construction including load bearing structure and floor finishing
    """
    def __init__(self, slab: Slab, floor: Floor):
        self.slab = slab
        self.floor = floor

    def structural_dead_load(self) -> float:
        """
        Total structural dead load of the slab construction [kN/m²].
        """
        return (
            self.slab.self_load()
        )

    def non_structural_dead_load(self) -> float:
        """
        Total non-structural dead load of the slab construction [kN/m²].
        """
        return (
            self.slab.infill_load()
            + self.floor.dead_load()
        )