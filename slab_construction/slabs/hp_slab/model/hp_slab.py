from typing import Optional
from structuralcodes.sections import GenericSection
from core.unit_core import mm2_to_m2, mm3_to_m3
from slab_construction.slab_construction import FloorMaterial
from slab_construction.slabs.one_way_slab import OneWaySlab
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell


class HPSlab(OneWaySlab):
    def __init__(
            self,
            hp_shell: HPShell,
            infill_material: FloorMaterial,
            name: Optional[str] = None,
    ):
        """
        Author: Elliot Melcer
        Represents a hyperbolic paraboloid (hp) slab.
        """

        self.hp_shell = hp_shell
        self.infill_material = infill_material
        self.name = name

    @property
    def L(self) -> float:
        return self.hp_shell.hp_geometry.L

    @property
    def B(self) -> float:
        return self.hp_shell.hp_geometry.B

    def minimum_infill_volume(self):
        """
        Author: Jamila Loutfi
        Calculates the minimum infill volume to flatten out the top of an hp-shell
        """
        mid_surface_volume = abs(self.B * self.L * (-2 / 3 * self.hp_shell.hp_geometry.Hy - 1 / 3 * self.hp_shell.hp_geometry.Hx))

        min_infill_volume = mid_surface_volume - self.hp_shell.hp_geometry.volume() / 2

        return min_infill_volume

    def section_at(self, _x: float, name: Optional[str] = None) -> GenericSection:
        return self.hp_shell.section_at(_x, name)

    def self_load(self) -> float:
        """
        Author: Elliot Melcer
        Returns the self-weight load of the concrete shell in [kN/m²]
        Note: self-weight of CRFP-reinforcement is negligible
        """
        concrete_volume_m3 = mm3_to_m3(self.hp_shell.hp_geometry.volume())  # [m³]
        gamma_c = self.hp_shell.concrete.density * 10 / 1000                # [kN/m³]
        net_area = mm2_to_m2(self.B * self.L)                               # [m²]

        return concrete_volume_m3 * gamma_c / net_area                      # [kN/m²]

    def infill_load(self) -> float:
        """
        Author: Elliot Melcer
        Returns the load due to minimum infill on the slab in [kN/m²]
        """
        infill_volume_m3 = mm3_to_m3(self.minimum_infill_volume())  # [m³]
        gamma_c = self.infill_material.density * 10 / 1000          # [kN/m³]
        net_area = mm2_to_m2(self.B * self.L)                       # [m²]

        return infill_volume_m3 * gamma_c / net_area                # [kN/m²]

