from _mains.testing_files.testing_materials import reinforcement_B500, concrete_c40_uls
from dataclasses import dataclass
from structuralcodes.sections import GenericSection
from slab_construction.slabs.one_way_slab import OneWaySlab
from shapely.geometry import Polygon
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement

r"""
Author: Elliot Melcer

Class for testing the calculation of ultimate support moment:

System:
Two Span Beam with Bi-Linear Reinforcement Geometry (fictional)

 ------------------------------------------------------
|                        ======                        |
|                  ======      ======                  |
|            ======                  ======            |
|      ======                              ======      |
|======                                          ======|
 -------------------------------------------------------
 /\                         /\                         /\

"""

@dataclass(frozen=True)
class _GeomParams:
    b: float
    b1: float
    b0: float
    d: float
    d1: float
    cover: float

    @property
    def y_top(self) -> float:
        return self.d / 2

    @property
    def y_bottom(self) -> float:
        return -self.d / 2 - self.d1

    def polygon(self) -> Polygon:
        b = self.b
        b0 = self.b0
        d = self.d
        d1 = self.d1

        return Polygon(
            [
                (-b / 2,  d / 2),
                (-b / 2, -d / 2),
                (-b0 / 2, -d / 2),
                (-b0 / 2, -d / 2 - d1),
                ( b0 / 2, -d / 2 - d1),
                ( b0 / 2, -d / 2),
                ( b / 2, -d / 2),
                ( b / 2,  d / 2),
            ]
        )


class TestSlabTwoWay(OneWaySlab):
    def __init__(
            self,
            L: float,
            b: float = 300.0,
            b1: float = 50.0,
            b0: float = 200.0,
            d: float = 200.0,
            d1: float = 200.0,
            cover: float = 50.0,
            rebar_diam: float = 20.0,
    ) -> None:
        self._L = float(L)
        self._B = float(b)
        self._rebar_diam = float(rebar_diam)

        self._gp = _GeomParams(
            b=float(b),
            b1=float(b1),
            b0=float(b0),
            d=float(d),
            d1=float(d1),
            cover=float(cover),
        )

        self._poly = self._gp.polygon()

    @property
    def L(self) -> float:
        return self._L

    @property
    def B(self) -> float:
        return self._B

    def section_at(self, x: float) -> GenericSection:
        x = max(0.0, min(2.0, float(x)))

        y_top = self._gp.y_top
        y_bottom = self._gp.y_bottom
        c = self._gp.cover

        y_bot_reinf = y_bottom + c
        y_top_reinf = y_top - c

        t = abs(x - 1.0)  # 1 at x=0,2 and 0 at x=1
        y_reinf = y_top_reinf + (y_bot_reinf - y_top_reinf) * t

        geometry = SurfaceGeometry(poly=self._poly, material=concrete_c40_uls)

        b0 = self._gp.b0
        bar_diam = self._rebar_diam

        pts = (
            (-b0 / 2 + c, y_reinf),
            (0.0, y_reinf),
            (b0 / 2 - c, y_reinf),
        )

        for pt in pts:
            geometry = add_reinforcement(geometry, pt, bar_diam, reinforcement_B500)

        return GenericSection(geometry, integrator="marin", name = f"Section at {x*self._L/1000} m")

    def self_load(self) -> float:
        # implement as appropriate for your project
        return 0.0

    def infill_load(self) -> float:
        # implement as appropriate for your project
        return 0.0
