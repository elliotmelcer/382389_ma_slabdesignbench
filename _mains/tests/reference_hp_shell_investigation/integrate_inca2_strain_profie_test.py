import numpy as np
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_hp_sections import hp_ref
from _mains.testing_files.testing_materials import concrete_c50_uls, solidian_Q85_pre_37
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell

hp_shell = HPShell(hp_ref, concrete_c50_uls, solidian_Q85_pre_37, reinf_area=85)
section = hp_shell.section_at(0.5)

# Get section extents
_, _, zmin, zmax = section.geometry.calculate_extents()
depth = zmax - zmin

# INCA2 strain profile values
eps_top_inca = -0.0035
eps_bot_inca = 0.004978
chi_y_inca = -23.6774e-6  # Negative for sagging (sign convention)

# Calculate eps_0 for INCA2 profile
# eps_bot = eps_0 + chi_y * zmin
eps_0_inca = eps_bot_inca - chi_y_inca * zmin

strain_profile_inca = [eps_0_inca, chi_y_inca, 0.0]
N, My, Mz = section.section_calculator.integrate_strain_profile(strain_profile_inca)

print(f"N = {N:.2f}, My = {My:.2f}, Mz = {Mz:.2f}")

def get_reinforcement_forces(section: GenericSection, strain_profile: list) -> list[dict]:
    """
    Author: Elliot Melcer

    Given a strain profile, returns the force in each reinforcement bar.

    The strain at each bar is computed from the profile:
        eps(y, z) = eps_0 + chi_y * z + chi_z * y

    For prestressed bars, the total strain includes the initial (prestress) strain:
        eps_total = eps_ini + eps_bending

    The stress is then obtained from the bar's constitutive law, and the force is:
        F_s = sigma_s * A_s

    Args:
        section:        GenericSection object
        strain_profile: [eps_0, chi_y, chi_z]  — same convention as integrate_strain_profile

    Returns:
        List of dicts, one per reinforcement point geometry, each containing:
            - 'bar_index':   int   — index of bar in point_geometries
            - 'y':           float — y-coordinate of bar [mm]
            - 'z':           float — z-coordinate of bar [mm]
            - 'area':        float — cross-sectional area [mm²]
            - 'eps_ini':     float — initial (prestress) strain [-]
            - 'eps_bending': float — strain from the applied strain profile [-]
            - 'eps_total':   float — total strain used for stress lookup [-]
            - 'sigma_s':     float — stress from constitutive law [MPa]
            - 'F_s':         float — axial force in bar [N]  (+ tension, - compression)

    Raises:
        ValueError: If the section has no reinforcement point geometries.
    """
    eps_0, chi_y, chi_z = strain_profile

    geometry = section.geometry

    if not hasattr(geometry, 'point_geometries') or len(geometry.point_geometries) == 0:
        raise ValueError("Section has no reinforcement point geometries.")

    results = []

    for i, pg in enumerate(geometry.point_geometries):
        # Bar coordinates
        y_s = pg.point.x  # horizontal axis
        z_s = pg.point.y  # vertical axis (depth)

        # Area
        A_s = pg.area  # mm²

        # Initial strain (prestress); default to 0 if not present
        reinf = pg.material
        eps_ini = getattr(reinf, 'initial_strain', None) or 0.0

        # Bending strain from the applied strain profile
        eps_bending = eps_0 + chi_y * z_s + chi_z * y_s

        # Total strain seen by the bar's constitutive law
        eps_total = eps_ini + eps_bending

        # Stress from the constitutive law
        sigma_s = reinf.constitutive_law.get_stress(eps_total)

        # Force in bar
        F_s = sigma_s * A_s

        results.append({
            'bar_index':   i,
            'y':           y_s,
            'z':           z_s,
            'area':        A_s,
            'eps_ini':     eps_ini,
            'eps_bending': eps_bending,
            'eps_total':   eps_total,
            'sigma_s':     sigma_s,
            'F_s':         F_s,
        })

    return results

bar_forces = get_reinforcement_forces(section, strain_profile_inca)

for bar in bar_forces:
    print(f"Bar {bar['bar_index']+1}: "
          f"z={bar['z']:.1f} mm | "
          f"ε_total={bar['eps_total']*1e3:.3f}‰ | "
          f"σ_s={bar['sigma_s']:.1f} MPa | "
          f"F_s={bar['F_s']/1e3:.2f} kN")
# --- Sum of reinforcement forces ---
sum_F_s = sum(bar['F_s'] for bar in bar_forces)

print("\n--- Reinforcement force summary ---")
print(f"Sum of bar forces = {sum_F_s/1e3:.2f} kN")

print("Force under Prestress")
N_reinf = 2 * hp_ref.nt * hp_shell.reinf_area * solidian_Q85_pre_37.initial_strain * solidian_Q85_pre_37.ftk
print(f"N_reinf = {N_reinf:.2f}")

def get_concrete_compression_force(
        section: GenericSection,
        strain_profile: list,
        grid_spacing: float = 2.0
) -> dict:
    """
    Author: Elliot Melcer

    Given a strain profile, returns the compression force carried by the concrete
    by integrating over the section's surface geometry using a regular grid.

    This implementation is integrator-agnostic (works with both MarinIntegrator
    and FiberIntegrator) because it bypasses the section integrator entirely
    and works directly with the shapely polygons.

    For each grid fiber inside the concrete polygon:
        eps(y, z) = eps_0 + chi_y * z + chi_z * y
        sigma     = constitutive_law.get_stress(eps)
        dF        = sigma * fiber_area

    Fiber areas are scaled so that sum(fiber_areas) == polygon.area exactly,
    preserving the total cross-section area regardless of grid resolution.

    Args:
        section:        GenericSection object (any integrator)
        strain_profile: [eps_0, chi_y, chi_z] — same convention as integrate_strain_profile
        grid_spacing:   Regular grid spacing [mm]. Smaller = more accurate, slower.
                        Default 2.0 mm gives a good accuracy/speed balance.

    Returns:
        dict containing:
            - 'F_c':            float — total compression force [N]  (negative)
            - 'F_t':            float — total tension force [N]      (positive)
            - 'F_net':          float — net concrete force F_c + F_t [N]
            - 'z_c':            float — centroid z-coord of compression zone [mm]
            - 'n_fibers_c':     int   — fibers in compression
            - 'n_fibers_t':     int   — fibers in tension
            - 'n_fibers_total': int   — total fibers sampled

    Raises:
        ValueError: If no concrete surface geometry is found.
    """
    from shapely.geometry import Point as ShapelyPoint

    eps_0, chi_y, chi_z = strain_profile

    geometry = section.geometry

    # Collect all surface geometries (skip point geometries = rebar)
    if hasattr(geometry, 'geometries'):
        surface_geos = geometry.geometries        # CompoundGeometry
    else:
        surface_geos = [geometry]                 # plain SurfaceGeometry

    if not surface_geos:
        raise ValueError("No concrete surface geometry found in section.")

    # Accumulators
    F_c   = 0.0
    F_t   = 0.0
    Fz_c  = 0.0
    n_fibers_c = 0
    n_fibers_t = 0

    for surf_geo in surface_geos:
        poly        = surf_geo.polygon            # shapely Polygon
        law         = surf_geo.material.constitutive_law

        # --- Build regular grid over bounding box ---
        minx, minz, maxx, maxz = poly.bounds
        y_grid = np.arange(minx + grid_spacing / 2, maxx, grid_spacing)
        z_grid = np.arange(minz + grid_spacing / 2, maxz, grid_spacing)

        # Collect fiber centroids that fall inside the polygon
        fiber_y = []
        fiber_z = []
        for y_f in y_grid:
            for z_f in z_grid:
                if poly.contains(ShapelyPoint(y_f, z_f)):
                    fiber_y.append(y_f)
                    fiber_z.append(z_f)

        n_fibers = len(fiber_y)
        if n_fibers == 0:
            continue

        # Scale fiber area so that sum(areas) == polygon.area exactly
        fiber_area = poly.area / n_fibers

        # --- Integrate stress over fibers ---
        for y_f, z_f in zip(fiber_y, fiber_z):
            eps_f   = eps_0 + chi_y * z_f + chi_z * y_f
            sigma_f = law.get_stress(eps_f)
            dF      = sigma_f * fiber_area

            if sigma_f < 0.0:
                F_c  += dF
                Fz_c += dF * z_f
                n_fibers_c += 1
            elif sigma_f > 0.0:
                F_t += dF
                n_fibers_t += 1

    n_fibers_total = n_fibers_c + n_fibers_t

    z_c = (Fz_c / F_c) if F_c != 0.0 else float('nan')

    return {
        'F_c':            F_c,
        'F_t':            F_t,
        'F_net':          F_c + F_t,
        'z_c':            z_c,
        'n_fibers_c':     n_fibers_c,
        'n_fibers_t':     n_fibers_t,
        'n_fibers_total': n_fibers_total,
    }

cc = get_concrete_compression_force(section, strain_profile_inca)

print(f"Compression force:  F_c  = {cc['F_c']/1e3:>8.2f} kN")
print(f"Tension force:      F_t  = {cc['F_t']/1e3:>8.2f} kN")
print(f"Net force:          F_net= {cc['F_net']/1e3:>8.2f} kN")
print(f"Compression centroid: z_c = {cc['z_c']:.1f} mm")
print(f"Fibers: {cc['n_fibers_c']} compressed / {cc['n_fibers_t']} tensioned / {cc['n_fibers_total']} total")
