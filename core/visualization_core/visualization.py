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


# --- Moment-Curvature-Diagram ---

def plot_moment_curvature(m_c_res: MomentCurvatureResults, x = None, ax=None):
    """
            Author: Elliot Melcer
            Plot moment–curvature (M–K) diagram with My and Mu annotations.
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
        f"(K_u = {m_c_res.chi_y[-1] * 1e6 :.3e},\n"
        f" M_u = {m_c_res.m_y[-1] / 1e6:.3f} kNm)"
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
    ax.set_title(f"M-K-Diagram at x = {x} * L")

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

def plot_constitutive_law_concrete(concrete: Concrete, n: int = 100):
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

def plot_cross_section(gs: GenericSection, ax=None, x=None, **kwargs):
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
    ax.set_title(f"{gs.name} at x = {x} * L" if x is not None else f"{gs.name}")
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

