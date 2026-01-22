import numpy as np
from numpy import sqrt
from shapely import LineString, Polygon


class HPGeometry:
    def __init__(
            self,
            B: float,
            L: float,
            Hx: float,
            Hy: float,
            t: float,
            dy: float,
            nt: int,
    ):
        """
        Author: Elliot Melcer
        Represents a hyperbolic paraboloid (hp) shell.

        Parameters
        ----------
        B : float
            Width of the shell in mm
        L : float
            Length of the shell in mm
        Hx : float
            Rise (sag) in the x-direction in mm
        Hy : float
            Rise (sag) in the y-direction in mm
        t : float
            Thickness of the shell in mm
        dy : float
            Distance of the outermost tendon to the edge of the shell in mm
        nt: int
            Number of tendons per tendon group, total number of tendons: 2 * nt
        """
        self.B = float(B)
        self.L = float(L)
        self.Hx = float(Hx)
        self.Hy = float(Hy)
        self.t = float(t)
        self.dy = float(dy)
        self.nt = nt

    def _a(self):
        """
        Author: Jamila Loutfi
        returns geometry parameter a
        """
        a = self.L / (2 * sqrt(self.Hx))
        return a

    def _b(self) -> float:
        """
        Author: Jamila Loutfi
        returns geometry parameter b
        """
        b = self.B / (2 * sqrt(self.Hy))
        return b

    def _z(self, x: float, y: float) -> float:
        """
        Author: Jamila Loutfi
        returns z coordinate at given y coordinate of midline of shell
        """
        z = y**2 / self._b()**2 - x**2 / self._a()**2
        return z

    def x_p(self):
        """
        Author: Jamila Loutfi
        Returns the x-coordinate of the 4 Corner Points defining the Hyperbolic Paraboloid
        """
        x_p = self.L/2 * (1 + sqrt(self.Hy)/sqrt(self.Hx))
        return x_p

    def y_p(self):
        """
        Author: Jamila Loutfi
        Returns the y-coordinate of the 4 Corner Points defining the Hyperbolic Paraboloid
        """
        y_p = self.B/2 * (1 + sqrt(self.Hx)/sqrt(self.Hy))
        return y_p

    def z_p(self):
        """
        Author: Jamila Loutfi
        Returns the y-coordinate of the 4 Corner Points defining the Hyperbolic Paraboloid
        """
        z_p = (sqrt(self.Hx)+sqrt(self.Hy))**2
        return z_p

    def dy_real(self):
        """
        Author: Jamila Loutfi
        If nt = 1, calculate dy with alpha = 0.5
        else use the given dy
        """
        alpha_nt_1 = 0.5

        if self.nt == 1:
           dy_real = self.B / 2 + ((-self.L / 2) / self.x_p() + 2 * alpha_nt_1 - 1) * self.y_p()
           self.dy = dy_real
           print("dy_real=", dy_real)
           return dy_real
        else:
           return self.dy

    def alpha_edge(self):
        """
        Author: Jamila Loutfi
        Returns the alpha coordinate value of the outermost tendon near the edge of the shell
        """
        alpha_edge = 1/2 * ( (-self.B/2 + self.dy)/self.y_p() + (self.L/2)/self.x_p() + 1)
        return alpha_edge

    def alpha_edge_bar(self):
        """
        Author: Jamila Loutfi
        Returns the complementary alpha coordinate value of the outermost tendon near the edge of the shell
        """
        alpha_edge_bar = 1-self.alpha_edge()

        if self.alpha_edge() > 0.5:
            alpha_edge_bar = 0.5
        return alpha_edge_bar

    def delta_alpha(self):
        """
        Author: Jamila Loutfi
        Returns the distance between the tendons as alpha value
        """
        delta_alpha = (self.alpha_edge_bar() - self.alpha_edge()) / (self.nt - 1)
        return delta_alpha

    def alpha_list(self) -> list[float]:
        """
        Author: Jamila Loutfi
        Returns a list of alpha coordinates for all tendons in a tendon group
        """
        _alpha = self.alpha_edge() # local alpha variable that is subject to change if nt = 1

        if self.nt == 1:
            # if there is only one tendon, correct alpha value
            # 0.5 ist der richtige Wert
            _alpha = 0.5
            delta_alpha = 0
        else:
            delta_alpha = self.delta_alpha()

        alpha_list = []
        for i in range(self.nt):
            alpha_i = _alpha + delta_alpha * i
            alpha_list.append(alpha_i)

        return alpha_list

    def gt_x(self) -> tuple[list[float], list[float]]:
        """
        Author: Jamila Loutfi
        Returns a tuple of start and end x coordinates for a tendon group
        """
        gt_x_start = [-self.L/2] * self.nt
        gt_x_end = [self.L/2] * self.nt
        return   gt_x_start, gt_x_end

    def gt_y(self) -> tuple[list[float], list[float]]:
        """
        Author: Jamila Loutfi
        Returns a tuple of start and end y coordinates for a tendon group
        """
        gt_x_start, gt_x_end = self.gt_x()
        x_start, x_end = gt_x_start[0], gt_x_end[0]

        gt_y_start = []
        gt_y_end = []

        for alpha in self.alpha_list():
            y_st = (x_start / self.x_p() + 2 * alpha - 1) * self.y_p()
            gt_y_start.append(y_st)

            y_end = (x_end / self.x_p() + 2 * alpha - 1) * self.y_p()
            gt_y_end.append(y_end)

        return gt_y_start, gt_y_end

    def gt_z(self) -> tuple[list[float], list[float]]:
        """
        Author: Jamila Loutfi
        Returns a tuple of start and end z coordinates for a tendon group
        """
        gt_x_start, gt_x_end = self.gt_x()
        x_start, x_end = gt_x_start[0], gt_x_end[0]

        gt_z_start = []
        gt_z_end = []


        for alpha in self.alpha_list():
            z_st = (4 * alpha * x_start / self.x_p() - 2 * x_start / self.x_p() + 4 * alpha**2 - 4 * alpha + 1) * self.z_p()
            gt_z_start.append(z_st)

            z_end = (4 * alpha * x_end   / self.x_p() - 2 * x_end   / self.x_p() + 4 * alpha**2 - 4 * alpha + 1) * self.z_p()
            gt_z_end.append(z_end)

        return gt_z_start, gt_z_end

    def tendons(self) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
        """
        Author: Elliot Melcer
        Returns tendons as a list of tuples containing the start and end coordinates as tuples
        """
        gt_x_start, gt_x_end = self.gt_x()
        gt_y_start, gt_y_end  = self.gt_y()
        gt_z_start, gt_z_end = self.gt_z()

        tendon_list = []

        # regular tendon group
        for xs, xe, ys, ye, zs, ze in zip(gt_x_start, gt_x_end, gt_y_start, gt_y_end, gt_z_start, gt_z_end):
            start_point = (xs, ys, zs)
            end_point = (xe, ye, ze)
            tendon_list.append((start_point, end_point))

        # mirrored tendon group
        for xs_m, xe_m, ys_m, ye_m, zs_m, ze_m in zip(reversed(gt_x_start), reversed(gt_x_end), reversed(gt_y_start), reversed(gt_y_end), reversed(gt_z_start), reversed(gt_z_end)):
            start_point_m = (xs_m, -ys_m, zs_m)
            end_point_m = (xe_m, -ye_m, ze_m)
            tendon_list.append((start_point_m, end_point_m))

        return tendon_list

    def tendon_coords_at_x(self, x: float) -> list[tuple[float, float]]:
        """
        Author: Elliot Melcer
        Returns tendon coordinates in cross-section plane at given coordinate x through linear interpolation
        """
        tendon_list = self.tendons()

        coords = []
        for (x0, y0, z0), (x1, y1, z1) in tendon_list:

            t = (x*self.L - x0) / (x1 - x0)  # linear interpolation parameter

            y = y0 + t * (y1 - y0)
            z = z0 + t * (z1 - z0)

            coords.append((y, z))

        return coords

    def midline(self, x: float, n: int) -> LineString:
        """
        Author: Elliot Melcer
        Returns a Shapely LineString representing the mid-surface
        polyline at coordinate x using n points.

        Parameters
        ----------
        x : float
            Longitudinal coordinate (centered at x = 0)
        n : int
            Number of points along the polyline

        Returns
        -------
        LineString
            Shapely LineString of (y, z) coordinates
        """
        a = self._a()
        b = self._b()
        hy = self.Hy

        # Half-span in y at this x
        y_max = self.B / 2

        # Sample nt points along y
        ys = [(-y_max + 2 * y_max * i / (n - 1)) for i in range(n)]

        # Compute z(y)
        zs = [self._z(x, y) for y in ys]

        # Build LineString
        return LineString(zip(ys, zs))

    def polygon_section_at(self, x: float, n: int) -> Polygon:
        """
        Author: Elliot Melcer
        Returns a shapely Polygon representing the cross-section at a given Factor x ∈ [-0,5 ; 0.5]
        (0.00 at middle of span). The polygon thickness t is applied perpendicular
        to the mid-surface. nt points are generated on the bottom and top edges.
        """
        # Compute local half-span in y for this x
        a = self._a()
        b = self._b()

        # y max from shell boundary
        y_max = self.B / 2

        # Sample nt points along y
        ys = [(-y_max + 2 * y_max * i / (n - 1)) for i in range(n)]

        # Mid-surface z-values
        zs_mid = [self._z(x*self.L, y) for y in ys]

        # Normal directions in 2D (y,z) plane
        normals = []
        for y in ys:
            dzdy = (2 * y) / (b**2)
            length = sqrt(dzdy**2 + 1)
            ny = -dzdy / length   # y-component of unit normal
            nz = 1 / length       # z-component of unit normal
            normals.append((ny, nz))

        # Offset points for bottom and top layers (± t/2)
        t2 = self.t / 2
        bottom = [(ys[i] - normals[i][0] * t2,
                   zs_mid[i] - normals[i][1] * t2)
                  for i in range(n)]

        top = [(ys[i] + normals[i][0] * t2,
                zs_mid[i] + normals[i][1] * t2)
               for i in range(n)]

        # Polygon ordering: bottom L→R, then top R→L
        poly_points = bottom + top[::-1]

        return Polygon(poly_points)


    def volume(self):
        """
        Author: Jamila Loutfi
        Calculates the concrete volume of an hp shell
        Übernommen von Pauls Skript "volumen.gh"
        """
        y1 = self.B / 2
        y2 = -self.B / 2

        b1 = (8 * self.Hy * y1 * np.sqrt(64 * self.Hy ** 2 * y1 * y1 / (self.B ** 4) + 1) + self.B ** 2 * np.asinh(
            8 * self.Hy * y1 / (self.B ** 2))) / (16 * self.Hy)
        b2 = (8 * self.Hy * y2 * np.sqrt(64 * self.Hy ** 2 * y2 ** 2 / (self.B ** 4) + 1) + self.B ** 2 * np.asinh(
            8 * self.Hy * y2 / (self.B ** 2))) / (16 * self.Hy)

        b = b1 - b2

        x1 = self.L / 2
        x2 = -self.L / 2

        l1 = (8 * self.Hx * x1 * np.sqrt(64 * self.Hx ** 2 * x1 * x1 / (self.L ** 4) + 1) + self.L **2 * np.asinh(
            8 * self.Hx * x1 / (self.L ** 2))) / (16 * self.Hx)
        l2 = (8 * self.Hx * x2 * np.sqrt(64 * self.Hx ** 2 * x2 * x2 / (self.L ** 4) + 1) + self.L ** 2 * np.asinh(
            8 * self.Hx * x2 / (self.L ** 2))) / (16 * self.Hx)

        l = l1 - l2

        volume = l * b * self.t
        # volumen = 1
        return volume