import math
from itertools import pairwise
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

        Note: reinf_area in [mm²]
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

    def total_reinforcement_volume(self) -> float:
        """
        Author: Elliot Melcer
        Returns the total reinforcement volume of a hp-shell in mm³
        """
        total_tendon_length = 0.0
        for (xs, ys, zs), (xe, ye, ze) in self.hp_geometry.tendons():
            total_tendon_length += math.dist((xs, ys, zs), (xe, ye, ze))  # Euclidean distance

        volume = total_tendon_length * self.reinf_area
        return volume

    def d_p(self) -> float:
        """
        Author: Elliot Melcer
        Returns the diameter of the reinforcement section in mm.
        """
        d_reinf = np.sqrt(4 * self.reinf_area / np.pi)

        return d_reinf

    def c_1_clear_concrete_cover(self) -> float:
        """
        Adapted from: Jamila Loutfi
        Returns available clear concrete cover along the midline from the
        outermost reinforcement to the edge at the HP-Shell Support
        """
        B = self.hp_geometry.B
        d_p = self.d_p()
        y_starts, _ = self.hp_geometry.gt_y()

        # include boundary y=-B/2 as starting point
        s_start = self.arc_length(-B / 2)

        s_first = self.arc_length(y_starts[0])

        c_1 = abs(s_start - s_first)

        if c_1 - d_p/2 < 0:
            c_1_clear = 0
        else:
            c_1_clear = c_1 - d_p/2

        return c_1_clear

    def s_min_clear_reinf_spacing(self) -> float:
        """
        Adapted from: Jamila Loutfi
        Returns the minimum available clear spacing between reinforcements along the hp_shell midline
        """
        d_p = self.d_p()
        y_starts, _ = self.hp_geometry.gt_y()
        y_starts_mirrored = [-y for y in y_starts[::-1]]
        y_starts_complete = y_starts + y_starts_mirrored

        # arc-lengths relative to y=0
        s_vals = [self.arc_length(yi) for yi in y_starts_complete]

        # pairwise distances: y[0]->y[1], ... , y[n-1]->y[n]
        s = [abs(b - a) for a, b in pairwise(s_vals)]

        s_min = min(s)

        if s_min - d_p < 0:
            s_min_clear = 0
        else:
            s_min_clear = s_min - d_p

        return s_min_clear

    def arc_length(self, y:float) -> float:
        """
        Adapted from: Jamila Loutfi
        Returns the arclength from the neutral z-axis to the given y-coordinate.
        Note: s_y is negative for y < 0 and positive for y > 0
        """

        b = self.hp_geometry.param_b()

        s_y = 1 / 4 * (2 * y * math.sqrt(((4 * y ** 2) / b ** 4) + 1) + b ** 2 * math.asinh((2 * y) / b ** 2))

        return s_y