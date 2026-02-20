from dataclasses import dataclass

from structuralcodes.core.base import Material


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
    Instantiable Simple Material for generic floor layers.
    """
    def __init__(self, density: float, name: str | None = "FloorMaterial") -> None:
        super().__init__(density=density, name=name)

class ScreedMaterial(Material):
    """
        Author: Elliot Melcer
        Instantiable Material for screed layers.
        """
    def __init__(self, density: float, name: str | None = "ScreedMaterial") -> None:
        super().__init__(density=density, name=name)

class InfillMaterial(Material):
    """
    Author: Elliot Melcer
    Instantiable Material for infill layers.
    """
    def __init__(self, density: float, name: str | None = "InfillMaterial") -> None:
        super().__init__(density=density, name=name)

class InsulationMaterial(Material):
    """
    Author: Elliot Melcer
    Instantiable Simple Material for insulation layers.
    """
    def __init__(self, density: float, E_dyn: float, name: str | None = "InsulationMaterial") -> None:
        super().__init__(density=density, name=name)
        self.E_dyn = E_dyn

class Floor:
    """
    Author: Elliot Melcer
    Class to model a floor construction made up of floor layers
    """
    def __init__(self, layers: list[FloorLayer] | None = None) -> None:
        self.layers: list[FloorLayer] = list(layers) if layers is not None else []

    def add_layer(self, material: Material, thickness: float) -> None:
        """
        Adds a layer to the floor construction.
        Note: Thickness in [mm] to keep in line with all other dimensions in structuralcodes
        Raises:
            ValueError: If thickness is not positive.
            ValueError: If a layer with the same material type already exists in the floor.
        """
        if thickness <= 0:
            raise ValueError("Thickness must be positive")

        material_type = type(material)
        if any(isinstance(layer.material, material_type) for layer in self.layers):
            raise ValueError(
                f"A layer with material type '{material_type.__name__}' already exists in this floor. "
                f"Only one layer per material type is permitted."
            )

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

    def get_layer_by_type(self, material_type: type) -> FloorLayer:
        """
        Returns the FloorLayer whose material is an instance of *material_type*.

        Args:
            material_type: A Material subclass, e.g. InsulationMaterial,
                           ScreedMaterial, InfillMaterial, FloorMaterial.

        Raises:
            KeyError: If no layer with the requested material type exists.

        """
        for layer in self.layers:
            if isinstance(layer.material, material_type):
                return layer
        raise KeyError(
            f"No floor layer with material type '{material_type.__name__}' found."
        )