"""
HP Shell Geometry Test - Final Working Version
Authors: Elliot Melcer, Jamila Loutfi
"""

from matplotlib import pyplot as plt
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_materials import concrete_c50_uls, solidian_Q142_pre_60
from core.visualization_core.visualization import (
    plot_constitutive_law_concrete,
    plot_constitutive_law_reinforcement,
    plot_cross_section
)

from slab_construction.slabs import HPSlab

# Import improved M-K plot for CFRP
import numpy as np

def plot_moment_curvature_cfrp(m_c_res, _x=None, ax=None):
    """Quick version of improved CFRP M-K plot"""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    chi = -np.array(m_c_res.chi_y) * 1e6
    m = -np.array(m_c_res.m_y) / 1e6

    ax.plot(chi, m, 'k-', linewidth=2, label="M–K curve")
    ax.scatter(chi, m, s=20, c='purple', alpha=0.5, label="Points")

    # Ultimate point
    ax.plot(chi[-1], m[-1], 'ro', markersize=10, label='Ultimate')
    ax.annotate(f'M_u={m[-1]:.2f} kNm\nκ_u={chi[-1]:.2e}',
                xy=(chi[-1], m[-1]), xytext=(-80, -20),
                textcoords='offset points', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='red'),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))

    ax.set_xlabel("Curvature κ [1/km]", fontsize=12)
    ax.set_ylabel("Moment M [kNm]", fontsize=12)
    ax.set_title(f"M-κ Diagram at x={_x:.2f}L" if _x else "M-κ Diagram",
                 fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

    return ax





def calculate_cracking_moment_manual(section):
    """
    Manual calculation of cracking moment.
    Workaround for structuralcodes library limitation.

    M_cr = f_ctm * W_y
    """

    # For CompoundGeometry, get material from the first surface geometry
    geometry = section.geometry
    if hasattr(geometry, 'geometries'):
        # CompoundGeometry - get concrete from first surface
        concrete = geometry.geometries[0].material
    else:
        # Simple SurfaceGeometry
        concrete = geometry.material

    # Try to get fctm - could be property, method, or attribute
    if hasattr(concrete, 'fctm'):
        fctm_attr = getattr(concrete, 'fctm')
        if callable(fctm_attr):
            fctm = fctm_attr()
        else:
            fctm = fctm_attr
    else:
        raise ValueError("No tensile strength available")

    # Get section properties
    gross_props = section.gross_properties

    # Try to get elastic section modulus directly
    if hasattr(gross_props, 'wy'):
        Wy = abs(gross_props.wy)
    elif hasattr(gross_props, 'Wy'):
        Wy = abs(gross_props.Wy)
    else:
        # Calculate manually
        # Get second moment of area
        if hasattr(gross_props, 'iyy'):
            iyy = gross_props.iyy  # second moment of inertia
        else:
            raise ValueError("Cannot find second moment of area")

        # Get distance to extreme fiber
        geom = section.geometry
        _, _, zmin, zmax = geom.calculate_extents()
        cz = gross_props.cz if hasattr(gross_props, 'cz') else 0
        z_t = zmin - cz

        Wy = abs(iyy / z_t)

    # Cracking moment
    M_cr = fctm * Wy  # N·mm

    print(f"  Manual calculation: f_ctm={fctm:.2f} MPa, W_y={Wy:.2e} mm³")

    return M_cr


# ============================================================
# GEOMETRY PARAMETERS
# ============================================================
b = 1200      # mm - width
l = 6750      # mm - length
hx = 70       # mm - rise in x-direction
hy = 280      # mm - rise in y-direction
t = 40        # mm - shell thickness
dy = 30       # mm - tendon edge distance
nt = 5        # - number of tendons per group

# Analysis position
x = 0.0  # * l

# ============================================================
# CREATE HP SHELL
# ============================================================
print("=" * 60)
print("HP SHELL STRUCTURAL ANALYSIS")
print("=" * 60)
print(f"\nGeometry:")
print(f"  Width (B) = {b} mm")
print(f"  Length (L) = {l} mm")
print(f"  Rise Hx = {hx} mm")
print(f"  Rise Hy = {hy} mm")
print(f"  Thickness = {t} mm")
print(f"  Number of tendons = {2*nt}")
print(f"  Analysis at x = {x} mm = {x/l:.1f}L")

hp = HPSlab(B=b, L=l, Hx=hx, Hy=hy, t=t, dy=dy, nt=nt)

# ============================================================
# CREATE SECTION GEOMETRY
# ============================================================
print("\nCreating section geometry...")

# Concrete section
hp_geometry = SurfaceGeometry(
    poly=hp.polygon_section_at(x=x, n=100),
    material=concrete_c50_uls
)

# Add reinforcement (CFRP tendons)
reinforcement_points = hp.tendon_coords_at_x(x=x)
diameter = 3.56825  # mm

for pt in reinforcement_points:
    hp_geometry = add_reinforcement(
        hp_geometry,
        pt,
        diameter,
        solidian_Q142_pre_60
    )

print(f"  Added {len(reinforcement_points)} CFRP tendons (Ø{diameter:.2f} mm)")

# ============================================================
# CREATE SECTION AND ANALYZE
# ============================================================
print("\nCreating section and calculating responses...")

hp_section = GenericSection(hp_geometry)
moment_curvature = hp_section.section_calculator.calculate_moment_curvature()

print("  ✓ Moment-curvature calculated successfully")

# Try to calculate cracking moment
try:
    # Try library method first
    m_cr = hp_section.section_calculator.calculate_cracking_moment(n=0)
    print(f"  ✓ Cracking moment: {m_cr/1e6:.2f} kNm")
except:
    # Use manual calculation as fallback
    try:
        m_cr = calculate_cracking_moment_manual(hp_section)
        print(f"  ✓ Cracking moment (manual): {m_cr/1e6:.2f} kNm")
    except Exception as e:
        print(f"  ⚠ Could not calculate cracking moment: {e}")

# ============================================================
# RESULTS SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)

# Ultimate moment
M_u = moment_curvature.m_y[-1]
K_u = moment_curvature.chi_y[-1]
print(f"\nUltimate capacity:")
print(f"  M_u = {M_u/1e6:.2f} kNm")
print(f"  K_u = {K_u*1e6:.3e} [1/1000m]")

# Yielding moment - NOT APPLICABLE FOR CRFP
# CRFP is brittle and doesn't yield like steel
if len(moment_curvature.m_y) >= 20:
    print(f"\nNote: CFRP reinforcement is brittle (no yielding)")
    print(f"      Failure occurs at ultimate capacity without ductile behavior")

# ============================================================
# VISUALIZATIONS
# ============================================================
print("\nGenerating plots...")

# 1. Constitutive laws
fig1 = plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plot_constitutive_law_concrete(concrete_c50_uls)
plt.subplot(1, 2, 2)
plot_constitutive_law_reinforcement(solidian_Q142_pre_60)
plt.tight_layout()

# 2. Cross-section
fig2, ax2 = plt.subplots(figsize=(10, 8))
plot_cross_section(hp_section, x=x/l, ax=ax2)

# 3. M-K diagram (improved for CFRP)
fig3, ax3 = plt.subplots(figsize=(10, 8))
plot_moment_curvature_cfrp(moment_curvature, x=x/l, ax=ax3)

# 4. Results table (optional - uncomment if needed)
# print("\n" + "=" * 60)
# print("DETAILED M-K RESULTS")
# print("=" * 60)
# print(table_moment_curvature(moment_curvature))

print("\n✓ All plots generated successfully")
print("=" * 60)

plt.show()