import numpy as np
from matplotlib.collections import PolyCollection
from shapely.geometry.polygon import Polygon
from structuralcodes.core._section_results import MomentCurvatureResults
from structuralcodes.core.base import ConstitutiveLaw
from structuralcodes.geometry import Geometry
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.reinforcement import Reinforcement
from structuralcodes.sections import GenericSection
from tabulate import tabulate
import typing as t
import matplotlib.pyplot as plt

from core.analysis_core.section_methods import get_strain_at_point


def plot_moment_curvature(m_c_res: MomentCurvatureResults, x = None, ax=None, title = ""):
    """
    Author: Elliot Melcer
    Plot moment–curvature (M–K) diagram with My and Mu annotations.

    :param m_c_res:     MomentCurvatureResults object from structuralcodes library
    :param x:           Relative position along the Beam x∈[0,1]
    :param ax:          The axes with the plot.
    :param title:       Optional title
    :return:
    """

    import matplotlib.pyplot as plt

    # Create figure/axes if not provided
    if ax is None:
        fig, ax = plt.subplots()

    # ============================================================
    #              Plot continuous M–K curve
    # ============================================================
    ax.plot(-m_c_res.chi_y * 1e6, -m_c_res.m_y / 1e6,
            color="black", linewidth=1.5, label="M–K curve")

    # ============================================================
    #              Plot ALL points as small purple dots
    # ============================================================
    ax.scatter(-m_c_res.chi_y * 1e6, -m_c_res.m_y / 1e6,
               s=6, color="purple", label="M–K points")

    # ============================================================
    #                    ULTIMATE POINT (Mu)
    # ============================================================
    x_u = -m_c_res.chi_y[-1] * 1e6
    y_u = -m_c_res.m_y[-1] / 1e6

    # Dot
    ax.plot(x_u, y_u, 'ro', markersize=5)

    # Label
    label_u = (
        f"(K_u = {-m_c_res.chi_y[-1] * 1e6 :.3e},\n"
        f" M_u = {-m_c_res.m_y[-1] / 1e6:.3f} kNm)"
    )
    ax.text(
        x_u, y_u, label_u,
        fontsize=10, color="red",
        ha="right", va="bottom"
    )

    # --- Axis labels ---
    ax.set_xlabel("K [1/1000m]")
    ax.set_ylabel("My [kNm]")

    # --- Grid ---
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

    # ---- Add title here ----
    ax.set_title(f"{title} \n M-K-Diagram at x = {x} * L")

    return ax

def plot_moment_curvature_with_reference(
    m_c_res: MomentCurvatureResults,
    ref_curvatures,
    ref_moments,
    x=None,
    ax=None,
    title="",
    ref_label="",
):
    """
    Author: Elliot Melcer
    Plot moment–curvature (M–K) diagram from m_c_res and superimpose
    a second M–K dataset given as curvature and moment lists.

    Parameters
    ----------
    m_c_res : MomentCurvatureResults
        Object containing chi_y and m_y arrays.
    ref_curvatures : list or array
        Reference curvature values.
    ref_moments : list or array
        Reference moment values.
    x : float, optional
        Position factor for title.
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on.
    title : str, optional
        Plot title prefix.
    ref_label : str, optional
        Label for reference dataset.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the plot.
    """

    import matplotlib.pyplot as plt
    import numpy as np

    # Convert reference data to arrays
    ref_curvatures = np.asarray(ref_curvatures, dtype=float)
    ref_moments = np.asarray(ref_moments, dtype=float)

    if len(ref_curvatures) != len(ref_moments):
        raise ValueError("ref_curvatures and ref_moments must have the same length.")

    # Create figure/axes if not provided
    if ax is None:
        fig, ax = plt.subplots()

    # ============================================================
    #                  Plot main M–K curve
    # ============================================================
    ax.plot(
        -m_c_res.chi_y * 1e6,
        -m_c_res.m_y / 1e6,
        color="black",
        linewidth=1.0,
        label="M–K curve (Python)",
    )

    ax.scatter(
        -m_c_res.chi_y * 1e6,
        -m_c_res.m_y / 1e6,
        s=2,
        color="black",
    )

    # ============================================================
    #                  Plot reference M–K dataset
    # ============================================================

    if len(ref_curvatures) == 1:
        ref_marker_size = 6.0
    else:
        ref_marker_size = 0.0

    ax.plot(
        ref_curvatures * 1e3,
        ref_moments,
        linewidth=1.0,
        marker="x",
        markersize=ref_marker_size,
        label=ref_label,
    )

    # ============================================================
    #                    ULTIMATE POINT (Mu)
    # ============================================================
    x_u = -m_c_res.chi_y[-1] * 1e6
    y_u = -m_c_res.m_y[-1] / 1e6

    ax.plot(x_u, y_u, "ro", markersize=5)

    label_u = (
        f"(K_u = {-m_c_res.chi_y[-1] * 1e6:.3e},\n"
        f" M_u = {-m_c_res.m_y[-1] / 1e6:.3f} kNm)"
    )
    ax.text(
        x_u,
        y_u,
        label_u,
        fontsize=10,
        color="red",
        ha="right",
        va="bottom",
    )

    # --- Axis labels ---
    ax.set_xlabel("K [1/1000m]")
    ax.set_ylabel("My [kNm]")

    # --- Grid ---
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)

    # --- Legend ---
    ax.legend()

    # --- Title ---
    ax.set_title(f"{title}\nM-K-Diagram at x = {x} * L")

    return ax

from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.axes


@dataclass
class MomentCurvatureLine:
    """
    Author: Elliot Melcer
    Container for a single moment–curvature dataset to be plotted.

    Attributes
    ----------
    moments : list or array
        Moment values [kNm].
    curvatures : list or array
        Curvature values.
    name : str
        Legend label for this line.
    color : str
        Matplotlib color string (e.g. "black", "#FF0000", "tab:blue").
    linestyle : str
        Matplotlib linestyle string (e.g. "solid", "dashed", "dotted",
        "dashdot") or shorthand ("-", "--", ":", "-.").
    linewidth : float
        Line width. Defaults to 1.0.
    marker : str
        Matplotlib marker string (e.g. "x", "o", ""). Defaults to "".
    markersize : float
        Marker size. Defaults to 4.0.
    """

    moments: list
    curvatures: list
    name: str
    color: str = "black"
    linestyle: str = "solid"
    linewidth: float = 1.0
    marker: str = ""
    markersize: float = 4.0

    def __post_init__(self):
        self.moments = np.asarray(self.moments, dtype=float)
        self.curvatures = np.asarray(self.curvatures, dtype=float)
        if len(self.moments) != len(self.curvatures):
            raise ValueError(
                f"MomentCurvatureLine '{self.name}': "
                "'moments' and 'curvatures' must have the same length "
                f"({len(self.moments)} vs {len(self.curvatures)})."
            )

    @classmethod
    def from_results(
            cls,
            m_c_res: MomentCurvatureResults,
            name: str,
            color: str = "black",
            linestyle: str = "solid",
            linewidth: float = 1.0,
            marker: str = "",
            markersize: float = 4.0,
    ) -> "MomentCurvatureLine":
        """
        Construct a MomentCurvatureLine from a MomentCurvatureResults object,
        applying the standard unit conversions:
            curvatures : chi_y  →  -chi_y * 1e6   [1/1000m]
            moments    : m_y    →  -m_y   / 1e6   [kNm]

        Parameters
        ----------
        m_c_res : MomentCurvatureResults
            Raw results object with chi_y [1/m] and m_y [Nm] arrays.
        name : str
            Legend label for this line.
        color, linestyle, linewidth, marker, markersize
            Forwarded directly to MomentCurvatureLine.
        """
        return cls(
            moments=-m_c_res.m_y / 1e6,
            curvatures=-m_c_res.chi_y * 1e6,
            name=name,
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            marker=marker,
            markersize=markersize,
        )


def plot_moment_curvature_multiple(
    lines: list[MomentCurvatureLine],
    ax: Optional[matplotlib.axes.Axes] = None,
    title: str = "",
    x: Optional[float] = None,
    xlabel: str = "Krümmung κ [1/1000m]",
    ylabel: str = "My [kNm]",
    xlim: Optional[tuple[float, float]] = None,
    ylim: Optional[tuple[float, float]] = None,
) -> matplotlib.axes.Axes:
    """
    Author: Elliot Melcer
    Plot multiple moment–curvature (M–K) datasets on a single axes.

    Parameters
    ----------
    lines : list[MomentCurvatureLine]
        One or more M–K datasets to plot, drawn in list order.
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on. A new figure/axes is created when omitted.
    title : str, optional
        Plot title prefix.
    x : float, optional
        Position factor appended to the title as ``"M-K-Diagram at x = {x} * L"``.
    xlabel : str, optional
        Label for the horizontal axis. Defaults to ``"K [1/1000m]"``.
    ylabel : str, optional
        Label for the vertical axis. Defaults to ``"My [kNm]"``.
    xlim : tuple[float, float], optional
        (x_min, x_max) axis limits. If omitted, matplotlib auto-scales.
    ylim : tuple[float, float], optional
        (y_min, y_max) axis limits. If omitted, matplotlib auto-scales.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes with the finished plot.

    Raises
    ------
    ValueError
        If *lines* is empty.
    """

    if not lines:
        raise ValueError("'lines' must contain at least one MomentCurvatureLine.")

    if ax is None:
        _, ax = plt.subplots()

    # --- Zero axes ---
    ax.axhline(0, color="#b0b0b0", linewidth=0.7, linestyle="solid", zorder=1)
    ax.axvline(0, color="#b0b0b0", linewidth=0.7, linestyle="solid", zorder=1)

    # --- Data lines ---
    for line in lines:
        ax.plot(
            line.curvatures,
            line.moments,
            color=line.color,
            linestyle=line.linestyle,
            linewidth=line.linewidth,
            marker=line.marker,
            markersize=line.markersize,
            label=line.name,
            zorder=2,
        )

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.yaxis.set_major_locator(plt.MultipleLocator(5))
    ax.grid(True, linestyle="-", linewidth=0.5, alpha=0.7)
    ax.legend(loc="lower right")

    full_title = title
    if x is not None:
        full_title = f"{title}\nM-K-Diagram at x = {x} * L"
    ax.set_title(full_title)

    return ax



def table_moment_curvature(m_c_res: MomentCurvatureResults):
        """
        Author: Elliot Melcer
        Return a tabulated string of moment–curvature results_c1_1.
        """
        # Convert to numpy arrays for safety
        chi_y = np.asarray(m_c_res.chi_y)
        chi_z = np.asarray(m_c_res.chi_z) if m_c_res.chi_z is not None else None
        eps_axial = np.asarray(m_c_res.eps_axial)
        m_y = np.asarray(m_c_res.m_y)
        m_z = np.asarray(m_c_res.m_z) if m_c_res.m_z is not None else None

        # Build table rows
        rows = []
        for i in range(len(chi_y)):
            rows.append([
                i,
                chi_y[i],
                chi_z[i] if chi_z is not None else None,
                eps_axial[i],
                m_y[i],
                m_z[i] if m_z is not None else None,
            ])

        headers = ["i", "chi_y", "chi_z", "eps_axial", "m_y", "m_z"]

        return tabulate(rows, headers=headers, floatfmt=".3e", tablefmt="fancy_grid")

# --- Concrete ---

def plot_constitutive_law_concrete(concrete: Concrete, n: int = 100, debug: bool = False):
    """
    Author: Elliot Melcer
    Plot the constitutive law (stress–strain curve) for this concrete material
    """

    if concrete.constitutive_law is None:
        raise ValueError("No constitutive law is attached to this Concrete instance.")

    law = concrete.constitutive_law

    # Build strain range based on law parameters if present
    eps_min, _ = law.get_ultimate_strain()
    eps_0 = getattr(law, "_eps_0", -0.002)

    eps = np.linspace(eps_min, -eps_min, n)
    sig = law.get_stress(eps)

    if debug:
        print(f"eps: {eps*1000}")
        print(f"sig: {sig}")

    # === FLIP OVER X AND Y AXIS ===
    eps_plot = -eps
    sig_plot = -sig

    fig, ax = plt.subplots()
    ax.plot(eps_plot, sig_plot, linewidth=1.8, color="black", label=law.name)

    ax.set_xlabel("Strain [-]")
    ax.set_ylabel("Stress [MPa]")
    ax.set_title(f"Constitutive Law of {concrete.name}")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

# --- Reinforcement ---

def plot_constitutive_law_reinforcement(reinforcement: Reinforcement, n: int = 100):
    """
            Author: Elliot Melcer
            Plot the reinforcement stress–strain constitutive law.

            No flipping of axes is performed. Positive strain → positive stress.
            """

    import numpy as np
    import matplotlib.pyplot as plt

    # Check constitutive law
    if reinforcement.constitutive_law is None:
        raise ValueError(
            "No constitutive law is attached to this Reinforcement instance."
        )

    law = reinforcement.constitutive_law

    # ------------------------------------------------------------
    #   Build strain domain for steel
    # ------------------------------------------------------------
    eps_y = reinforcement.epsyk  # yield strain
    eps_u = reinforcement.epsud()  # ultimate strain

    # Positive strain range typical for reinforcement
    eps = np.linspace(0.0, eps_u * 1.0, n)

    # Compute stresses (in MPa)
    sig = law.get_stress(eps)

    # ------------------------------------------------------------
    #   Plot
    # ------------------------------------------------------------
    fig, ax = plt.subplots()
    ax.plot(
        eps, sig,
        color="black", linewidth=1.8,
        label=f"{reinforcement.name} ({law.name})"
    )

    # ---------------------------------------------
    #   Axes & grid
    # ---------------------------------------------
    ax.set_xlabel("Strain [-]")
    ax.set_ylabel("Stress [MPa]")
    ax.set_title("Reinforcement Constitutive Law")
    ax.grid(True, linestyle="--", alpha=0.55)
    ax.legend()


# --- Cross Section ---

def plot_cross_section(gs: GenericSection, ax=None, x=None, title = "", **kwargs):
    """
    Author: Elliot Melcer
    Plot the section geometry, its centroid, and the local coordinate system.

    Parameters
    ----------
     ax : matplotlib.axes.Axes, optional
         Axis to draw on. If None, a new figure is created.
     x : float, optional longitudinal coordinate for title.
     kwargs : dict
         Extra args passed to geometry.plot().
     gs: GenericSection
         Generic section geometry.
     title: str, optional
         Additional title of the plot.
    """

    # Create axes if needed
    if ax is None:
        fig, ax = plt.subplots()

    # ---- 1. Plot the geometry using geometry method ----
    _plot_geometry(gs.geometry, ax=ax, x=x, **kwargs)

    # ---- 2. Plot the section centroid ----
    cy = gs.gross_properties.cy
    cz = gs.gross_properties.cz

    ax.scatter(cy, cz, color="red", s=10, zorder=10)
    ax.text(cy, cz, f" C({cy:.2f}, {cz:.2f})",
            color="red", va="bottom", ha="left")

    # ---- 3. Plot local coordinate system at (0,0) ----
    x_min, x_max, y_min, y_max = gs.geometry.calculate_extents()
    L = 0.1 * (y_max-y_min)

    # y-axis → positive x direction
    ax.arrow(0, 0, L, 0,
             head_width=L * 0.3, head_length=L * 0.3,
             fc="black", ec="black", alpha = 0.4)
    ax.text(L * 1.5, 0, "y", va="center", ha="left", color="black", alpha = 0.4)

    # z-axis → positive y direction
    ax.arrow(0, 0, 0, L,
             head_width=L * 0.3, head_length=L * 0.3,
             fc="black", ec="black", alpha = 0.4)
    ax.text(0, L * 1.5, "z", va="bottom", ha="center", color="black", alpha = 0.4)

    # ---- 4. Final formatting ----
    ax.set_title(f"{gs.name} at x = {x} * L" if x is not None else f"{gs.name} \n {title}")
    ax.set_aspect("equal")

    return ax

# --- Geometry ---

def _plot_geometry(geo: Geometry, ax=None, x = None, **kwargs):
    """
    Author: Elliot Melcer
    Plot any Geometry, SurfaceGeometry, PointGeometry, or CompoundGeometry object.

    Parameters
    ----------
    geo : Geometry
        The geometry object to plot.
    ax : matplotlib.axes.Axes, optional
        Existing axis to draw on. If None, a new figure is created.
    kwargs : dict
        Extra keyword arguments for styling (e.g. color="blue", linewidth=2).
    """

    if ax is None:
        fig, ax = plt.subplots()

    # Surface geometry
    if hasattr(geo, "polygon"):
        poly = geo.polygon
        _plot_polygon(poly, ax, **kwargs, edgecolor="grey", facecolor="lightgrey")

    # Point geometry
    if hasattr(geo, "point"):
        circ = geo.point.buffer(geo.diameter / 2)
        _plot_polygon(circ, ax, **kwargs, edgecolor="black", facecolor="black")

    # Compound geometry
    if hasattr(geo, "geometries"):
        for g in geo.geometries:
            _plot_geometry(g, ax=ax, show=False, **kwargs)
        for p in geo.point_geometries:
            _plot_geometry(p, ax=ax, show=False, **kwargs)

    ax.set_aspect("equal")

    # ---- Add title here ----
    ax.set_title(f"Cross-Section at x = {x} * L")

    # remove frame
    for spine in ax.spines.values():
        spine.set_visible(False)

    return ax

def _plot_polygon(poly: Polygon, ax, edgecolor="black", facecolor="lightgrey", **kwargs):
    """
    Author: Elliot Melcer
    Plot and fill a Shapely polygon (supports holes).
    """
    # --- Fill exterior ---
    x, y = poly.exterior.xy
    ax.fill(x, y, facecolor=facecolor, edgecolor=edgecolor)

    # --- Fill holes (white) ---
    for hole in poly.interiors:
        hx, hy = hole.xy
        ax.fill(hx, hy, facecolor="white", edgecolor=edgecolor, linestyle="--")


def plot_triangulated_mesh(triangulated_data: t.List[t.Tuple[np.ndarray, np.ndarray, np.ndarray, ConstitutiveLaw]], show_centroids=True):
    """
    Visualize triangulated fibers returned by FiberIntegrator.triangulate().

    Parameters
    ----------
    triangulated_data : list of tuples
        (x, y, area, constitutive_law)
    show_centroids : bool
        If True, draw centroid dots.
    """

    fig, ax = plt.subplots()

    # Map each material to a color index
    materials = {}
    cmap = plt.cm.get_cmap('tab10')
    color_index = 0

    for x, y, area, material in triangulated_data:

        # each "set" (x,y,area) contains multiple fibers but they all
        # come from one triangulated surface with one material
        if material not in materials:
            materials[material] = cmap(color_index)
            color_index += 1

        col = materials[material]

        # draw small scatter markers for centroids
        if show_centroids:
            ax.scatter(x, y, s=10, color=col)

    # legend by material name
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=c,
                   markersize=8, label=str(m))
        for m, c in materials.items()
    ]
    ax.legend(handles=legend_elements, title="Materials")

    ax.set_aspect('equal', 'box')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Triangulated Fibers (centroids)")


def plot_mesh_with_triangles(triangulated_data):
    fig, ax = plt.subplots()

    for (x, y, area, material, mesh) in triangulated_data:
        verts = mesh['vertices']
        tris = mesh['triangles']

        # create polygon array for PolyCollection
        polys = [verts[tri] for tri in tris]

        pc = PolyCollection(polys,
                            facecolors='none',
                            edgecolors='k',
                            linewidths=0.6)
        ax.add_collection(pc)

        # optional – show centroids
        ax.scatter(x, y, s=5, color='red')

    ax.set_aspect('equal', 'box')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Triangulated mesh")


def plot_strain_profile(results: dict):
    """
    Author: Elliot Melcer
    Plots Strain Profile for Moment Calculation Results
    """

    section = results['section']
    strain_profile = results["strain_profile"]

    # Section extents
    _, _, zmin, zmax = section.geometry.calculate_extents()
    depth = zmax - zmin

    # Section centroid
    cz = section.gross_properties.cz

    # Top & bottom fiber strains
    eps_top = get_strain_at_point(strain_profile, 0, zmax)
    eps_bot = get_strain_at_point(strain_profile, 0, zmin)

    # Reinforcement z-coordinates
    z_reinf = [pg.point.y for pg in section.geometry.point_geometries]

    # Reinforcement strains (from strain field, no prestress)
    eps_reinf = [
        get_strain_at_point(strain_profile, 0, z_s)
        for z_s in z_reinf
    ]

    # --- X-axis strain limits (‰) with padding ------------------------
    eps_vals = [0.0, eps_top * 1e3, eps_bot * 1e3]
    eps_min = min(eps_vals) - 0.15
    eps_max = max(eps_vals) + 0.15

    # --- Y-axis padding (5% of section depth) -------------------------
    z_pad = 0.05 * depth

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 8))

    # Thick vertical extent line
    ax.vlines(
        x=0.0,
        ymin=zmin,
        ymax=zmax,
        color="black",
        linewidth=2
    )

    # Concrete strain profile
    ax.plot(
        [eps_top * 1e3, eps_bot * 1e3],
        [zmax, zmin],
        color="black",
        linewidth=2
    )

    # Top & bottom strain lines (thick)
    ax.hlines(
        y=zmax,
        xmin=min(0.0, eps_top * 1e3),
        xmax=max(0.0, eps_top * 1e3),
        color="black",
        linewidth=2
    )

    ax.hlines(
        y=zmin,
        xmin=min(0.0, eps_bot * 1e3),
        xmax=max(0.0, eps_bot * 1e3),
        color="black",
        linewidth=2
    )

    # Centroid line (dash-dot)
    ax.hlines(
        y=cz,
        xmin=eps_min,
        xmax=eps_max,
        color="black",
        linewidth=1,
        linestyle="-."
    )

    # Reinforcement strains (RED)
    for z_s, eps_s in zip(z_reinf, eps_reinf):
        ax.hlines(
            y=z_s,
            xmin=0.0,
            xmax=eps_s * 1e3,
            color="red",
            linewidth=1.5
        )

        ax.annotate(
            f"{eps_s * 1e3:+.3f}‰",
            (eps_s * 1e3, z_s),
            textcoords="offset points",
            xytext=(5, 0),
            va="center",
            color="red"
        )

    # Top strain label (left)
    ax.annotate(
        f"{eps_top * 1e3:+.3f}‰",
        (eps_top * 1e3, zmax),
        textcoords="offset points",
        xytext=(-5, 0),
        ha="right",
        va="center",
        color="black"
    )

    # Bottom strain label (right)
    ax.annotate(
        f"{eps_bot * 1e3:+.3f}‰",
        (eps_bot * 1e3, zmin),
        textcoords="offset points",
        xytext=(5, 0),
        va="center",
        color="black"
    )

    # Axes formatting
    ax.axvline(0.0, color="black", linewidth=1)
    ax.set_xlabel("Strain ε [‰]")
    ax.set_ylabel("z [mm]")
    ax.set_title(f"Strain Profile for {section.name}")

    ax.grid(True, linestyle="--", linewidth=0.5)

    # Apply padded limits
    ax.set_xlim(eps_min, eps_max)
    ax.set_ylim(zmin - z_pad, zmax + z_pad)

    return fig, ax

