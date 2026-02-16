"""
Demonstrates gross_properties corruption after integration
"""
from structuralcodes import set_design_code
from structuralcodes.sections import GenericSection
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.materials.constitutive_laws import Elastic
from shapely import Polygon
import numpy as np

set_design_code('ec2_2004')

def create_test_geometry():
    """Helper to create consistent test geometry"""
    n_points = 100
    width = 200
    height = 400

    y_bottom = np.linspace(-width/2, width/2, n_points//2)
    z_bottom = -height/2 - 10 * np.sin(np.pi * y_bottom / width)

    y_top = np.linspace(width/2, -width/2, n_points//2)
    z_top = height/2 + 5 * np.sin(np.pi * y_top / width)

    points = list(zip(y_bottom, z_bottom)) + list(zip(y_top, z_top))
    return Polygon(points), width, height

def create_test_section():
    """Helper to create a fresh test section"""
    polygon, width, height = create_test_geometry()

    concrete = create_concrete(fck=50, constitutive_law='parabolarectangle',
                              alpha_cc=0.85, gamma_c=1.5)

    brittle_elastic = Elastic(230000, eps_u=0.012)
    reinforcement = create_reinforcement(
        fyk=2800, Es=230000, ftk=2800, epsuk=0.012,
        density=1340, constitutive_law=brittle_elastic,
        initial_strain=0.002, gamma_s=1.3
    )

    geometry = SurfaceGeometry(poly=polygon, material=concrete)
    for y_pos in [-70, -35, 0, 35, 70]:
        geometry = add_reinforcement(geometry, (y_pos, -height/2 + 50), 3.5, reinforcement)

    return GenericSection(geometry, integrator='marin')

print("=" * 70)
print("DEMONSTRATING BUG: gross_properties corruption after integration")
print("=" * 70)
print()

# ============================================================================
# TEST 1: Normal case (gross_properties accessed BEFORE analysis) - WORKS
# ============================================================================
print("=" * 70)
print("TEST 1: Access gross_properties BEFORE analysis (WORKS)")
print("=" * 70)

section1 = create_test_section()

# Pre-compute gross_properties
cy_before = section1.gross_properties.cy
print(f"Before analysis: cy = {cy_before:.2f}")

# Do analysis
result1 = section1.section_calculator.calculate_bending_strength(n=0)
print(f"Analysis: M_u = {result1.m_y/1e6:.2f} kNm")

# Access again (uses cached value)
cy_after = section1.gross_properties.cy
print(f"After analysis: cy = {cy_after:.2f}")
print("SUCCESS: Gross properties work fine when accessed before analysis\n")

# ============================================================================
# TEST 2: Bug case (gross_properties accessed AFTER analysis) - FAILS
# ============================================================================
print("=" * 70)
print("TEST 2: Access gross_properties AFTER analysis (BUG - FAILS)")
print("=" * 70)

section2 = create_test_section()

# Do analysis WITHOUT accessing gross_properties first
result2 = section2.section_calculator.calculate_bending_strength(n=0)
print(f"Analysis: M_u = {result2.m_y/1e6:.2f} kNm")

# NOW access gross_properties for FIRST TIME after analysis
print("Attempting to access gross_properties for first time after analysis...")
try:
    cy_corrupted = section2.gross_properties.cy
    print(f"cy = {cy_corrupted:.2f}")
    print("UNEXPECTED: Should have failed but didn't")
except RuntimeError as e:
    print(f"EXPECTED BUG: {e}")
print()

# ============================================================================
# WORKAROUND 1: Clear integration cache before accessing gross_properties
# ============================================================================
print("=" * 70)
print("WORKAROUND 1: Clear integration cache before accessing properties")
print("=" * 70)

section3 = create_test_section()

# Do analysis
result3 = section3.section_calculator.calculate_bending_strength(n=0)
print(f"Analysis: M_u = {result3.m_y/1e6:.2f} kNm")

# WORKAROUND: Clear integration cache
print("Clearing integration cache...")
if hasattr(section3.section_calculator, 'integration_data'):
    section3.section_calculator.integration_data = None

# Now access gross_properties
try:
    cy_fixed = section3.gross_properties.cy
    print(f"cy = {cy_fixed:.2f}")
    print("SUCCESS: Clearing cache prevents corruption\n")
except RuntimeError as e:
    print(f"FAILED: {e}\n")

# ============================================================================
# WORKAROUND 2: Always access gross_properties before analysis
# ============================================================================
print("=" * 70)
print("WORKAROUND 2: Force gross_properties computation before analysis")
print("=" * 70)

section4 = create_test_section()

# WORKAROUND: Access gross_properties early to force caching
print("Pre-computing gross_properties...")
_ = section4.gross_properties.cy  # Force computation and caching
print("Cached gross_properties")

# Do analysis
result4 = section4.section_calculator.calculate_bending_strength(n=0)
print(f"Analysis: M_u = {result4.m_y/1e6:.2f} kNm")

# Access gross_properties (uses cached value, no recomputation)
try:
    cy_cached = section4.gross_properties.cy
    print(f"cy = {cy_cached:.2f}")
    print("SUCCESS: Pre-caching prevents corruption\n")
except RuntimeError as e:
    print(f"FAILED: {e}\n")

# ============================================================================
# WORKAROUND 3: Use separate sections for analysis vs visualization
# ============================================================================
print("=" * 70)
print("WORKAROUND 3: Use separate sections for analysis vs properties")
print("=" * 70)

section5_analysis = create_test_section()
section5_visualization = create_test_section()  # Fresh copy

# Do analysis on one section
result5 = section5_analysis.section_calculator.calculate_bending_strength(n=0)
print(f"Analysis on section A: M_u = {result5.m_y/1e6:.2f} kNm")

# Access gross_properties on the other (clean) section
try:
    cy_clean = section5_visualization.gross_properties.cy
    print(f"Properties from clean section B: cy = {cy_clean:.2f}")
    print("SUCCESS: Using separate sections avoids corruption\n")
except RuntimeError as e:
    print(f"FAILED: {e}\n")