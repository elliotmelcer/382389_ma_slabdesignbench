from typing import Optional

import numpy as np
from numpy import sqrt
from shapely import LineString, Polygon
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.reinforcement import Reinforcement
from structuralcodes.sections import GenericSection

from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry


class HPShell:
    def __init__(
            self,
            hp_geometry: HPGeometry,
            concrete: Concrete,
            reinforcement: Reinforcement,
            reinf_area: float,
            name: Optional[str] = None,
    ):
        """
        Author: Elliot Melcer
        Represents a hyperbolic paraboloid (hp) shell.
        """
        self.hp_geometry = hp_geometry
        self.concrete = concrete
        self.reinforcement = reinforcement
        self.reinf_area = reinf_area
        self.name = name

    def section_at(self, x: float, name: Optional[str] = None) -> GenericSection:
        """
        Author: Elliot Melcer
        Returns the section from a hp-shell at x * L with given material properties and reinforcement area

        Note:
            Reinforcement Area in mm²
            x ∈ [0 ; 1] with 0.0 at first support, 1.0 at second support
        """
        # --- Input validation ---
        if not 0.0 <= x <= 1.0:
            raise ValueError(
                f"x must be between 0.0 and 1.0 (inclusive). Received {x}."
            )

        # Coordinate Transformation
        # External API uses x ∈ [0 ; 1], but internal geometry calculations use x ∈ [-0.5, 0.5]
        x_internal = x - 0.5

        # Concrete Geometry
        hp_geometry = SurfaceGeometry(
            poly=self.hp_geometry.polygon_section_at(x=x_internal, n=100), material=self.concrete
        )

        # Reinforcement Geometry
        reinforcement_points = self.hp_geometry.tendon_coords_at_x(x=x_internal)
        d = np.sqrt(4 * self.reinf_area / np.pi)

        # Add Reinforcement to Concrete Geometry
        for pt in reinforcement_points:
            hp_geometry = add_reinforcement(
                hp_geometry,
                pt,  # reinforcement points
                d,  # diameter [mm]
                self.reinforcement  # reinforcement material
            )

        if name is None:
            hp_section = GenericSection(hp_geometry, name = self.name)
        else:
            hp_section = GenericSection(hp_geometry, name=name)

        return hp_section