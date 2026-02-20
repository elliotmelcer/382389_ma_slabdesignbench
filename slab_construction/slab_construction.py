from dataclasses import dataclass
from typing import Dict

from structuralcodes.core.base import Material

from core.unit_core import mm2_to_m2, mm3_to_m3
from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab
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

class SlabConstruction:
    """
    Author: Elliot Melcer
    Class to model a complete slab construction including load bearing structure and floor finishing
    """
    def __init__(self, slab: Slab, floor: Floor):
        self.slab = slab
        self.floor = floor
        self.assert_infill_compatibility()

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

    def assert_infill_compatibility(self) -> None:
        """
        Asserts that the slab's infill material is the same object as the floor's
        infill layer material, if an infill layer is present in the floor.

        Note: This is only relevant if slab construction is instantiated manually.
        One must make sure to use the same infill object for both the slab and the floor layer

        Raises:
            ValueError: If an infill layer exists in the floor but its material
                        is not the same object as the slab's infill material.
        """
        floor_infill_layers = [
            layer for layer in self.floor.layers
            if isinstance(layer.material, InfillMaterial)
        ]
        if not floor_infill_layers:
            return

        floor_infill = floor_infill_layers[0].material
        slab_infill = self.slab.infill_material

        if floor_infill is not slab_infill:
            raise ValueError(
                f"Infill material mismatch: the floor's infill layer and the slab "
                f"must reference the same object.\n"
                f"  Slab infill:  '{slab_infill.name}'  (id={id(slab_infill)})\n"
                f"  Floor infill: '{floor_infill.name}'  (id={id(floor_infill)})"
            )

    def infill_area_density_kg_m2(self):
        """
        Returns the area density of the infill in [kg/m²]
        Handles HPShell special case with minimum infill to achieve flat top
        """
        infill_layer = self.floor.get_layer_by_type(InfillMaterial)

        # Reference Area
        if isinstance(self.slab, HPSlab):
            area_m2 = mm2_to_m2(self.slab.L * self.slab.B)
        else:
            area_m2 = 1.0

        # Infill Volume
        base_infill_volume_m3 = 0.0
            # base_infill_volume if hp_slab
        if isinstance(self.slab, HPSlab):
            base_infill_volume_m3 = mm3_to_m3(self.slab.minimum_infill_volume())

            # floor layer infill volume
        infill_layer_t_m = infill_layer.thickness / 1000
        floor_infill_volume_m3 = infill_layer_t_m * area_m2

        total_volume_m3 = base_infill_volume_m3 + floor_infill_volume_m3

        # Infill Material
        infill_mat = infill_layer.material
        infill_density_kg_m3 = infill_mat.density

        # infill area density
        infill_area_density_kg_m2 = total_volume_m3 * infill_density_kg_m3 / area_m2

        return infill_area_density_kg_m2

    def get_parameters(self) -> dict:
        """
        Author: Elliot Melcer
        Returns a dictionary containing all slab construction parameters
        organized by category: Geometry, Concrete, and Reinforcement.

        Note: This method assumes the slab is an HPSlab with an HPShell.
        """
        from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab

        # Initialize result dictionary
        params = {
            "geometry": {},
            "concrete": {},
            "reinforcement": {}
        }

        # --- Geometry Parameters ---
        if isinstance(self.slab, HPSlab):
            hp_shell = self.slab.hp_shell
            hp_geom = hp_shell.hp_geometry

            # Slab geometry
            H_ges = hp_geom.Hx + hp_geom.Hy

            params["geometry"] = {
                "span_L": hp_geom.L,  # mm
                "width_B": hp_geom.B,  # mm
                "height": H_ges,  # mm (Hx + Hy)
                "Hx_Hges": hp_geom.Hx / H_ges if H_ges > 0 else 0.0,  # ratio [-]
                "thickness": hp_geom.t,  # mm
                "nt": hp_geom.nt,  # number of tendons per group
                "dy": hp_geom.dy,  # mm
            }

            # --- Concrete Parameters ---
            concrete = hp_shell.concrete
            params["concrete"] = {
                "fck": concrete.fck  # MPa
            }

            # --- Reinforcement Parameters ---
            reinforcement = hp_shell.reinforcement

            # Get initial strain (prestress percentage)
            initial_strain = getattr(reinforcement, 'initial_strain', 0.0)
            if initial_strain is None:
                initial_strain = 0.0

            # Convert to percentage (strain is typically in absolute form)
            initial_strain_percentage = initial_strain * 100

            params["reinforcement"] = {
                "name": reinforcement.name if hasattr(reinforcement, 'name') else str(reinforcement),
                "initial_strain_percentage": initial_strain_percentage,  # %
                "cross_sectional_area": hp_shell.reinf_area  # mm²
            }

        # --- Floor Layer Thicknesses ---
        # Extract thicknesses from floor layers by material type
        thickness_infill = 0.0
        thickness_screed = 0.0
        thickness_insulation = 0.0

        for layer in self.floor.layers:
            material = layer.material
            material_name = getattr(material, 'name', '').lower() if hasattr(material, 'name') else ''

            # Check if it's an insulation material by type
            if isinstance(material, InsulationMaterial):
                thickness_insulation += layer.thickness
            # Otherwise check by name
            elif 'insulation' in material_name or 'insu' in material_name:
                thickness_insulation += layer.thickness
            elif 'screed' in material_name:
                thickness_screed += layer.thickness
            elif 'infill' in material_name:
                thickness_infill += layer.thickness

        params["geometry"]["thickness_infill"] = thickness_infill  # mm
        params["geometry"]["thickness_screed"] = thickness_screed  # mm
        params["geometry"]["thickness_insulation"] = thickness_insulation  # mm

        return params

    def print_parameters(self) -> None:
        parameters = self.get_parameters()

        # Print results
        print("\nReturned parameters:")
        print("-" * 40)

        print("[GEOMETRY]")
        for key, value in parameters["geometry"].items():
            print(f"  {key}: {value}")

        print("\n[CONCRETE]")
        for key, value in parameters["concrete"].items():
            print(f"  {key}: {value}")

        print("\n[REINFORCEMENT]")
        for key, value in parameters["reinforcement"].items():
            print(f"  {key}: {value}")

        print("")