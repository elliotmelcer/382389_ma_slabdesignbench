"""
Test file for deflection calculations
Author: Elliot Melcer
"""

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4, test_slab_construction_c1_1, \
    test_slab_construction_c1_2_c50, test_slab_construction_c1_2_c80, test_slab_construction_c1_3
from _mains.testing_files.testing_loads import test_loads
from core.analysis_core.statics import calculate_line_load
from core.analysis_core.statics.deformations import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces

"""
Calculate deflections for test slab construction under different load combinations
"""

# Tested Slab Construction
slab_construction = test_slab_construction_c1_3

print("=" * 70)
print("DEFLECTION CALCULATION TEST")
print("=" * 70)

# Slab properties
span_m = slab_construction.slab.L / 1000  # Convert mm to m
print(f"\nSlab Properties:")
print(f"  Span: {span_m:.2f} m")
print(f"  Width: {slab_construction.slab.B:.0f} mm")

# Load information
print(f"\nLoads:")
print(f"  Live load: {test_loads.Qk[0]:.1f} kN/m²")
print(f"  Self-weight: {slab_construction.structural_dead_load():.2f} kN/m²")
print(f"  Non-structural: {slab_construction.non_structural_dead_load():.2f} kN/m²")

# Calculate deflections
print(f"\n" + "=" * 70)
print("DEFLECTION RESULTS")
print("=" * 70)

# Fundamental combination
print("\n1. FUNDAMENTAL COMBINATION (ULS)")

q_fund = calculate_line_load(
    slab_construction=slab_construction,
    loads=test_loads,
    combination="FUNDAMENTAL")

deflection_fund = DeflectionCalculator.calculate_deflection(
    slab_construction=slab_construction,
    loads=test_loads,
    system="SIMPLE_BEAM",
    combination="FUNDAMENTAL",
    n_intervals=40,
    n_axial=0.0,
    debug=False
)

print(f"   q_fund: {q_fund:.2f} kN/m")
print(f"   Deflection: {deflection_fund:.2f} mm")
print(f"   Deflection/Span: L/{span_m * 1000 / deflection_fund:.0f}")

# Quasi-permanent combination
print("\n2. QUASI-PERMANENT COMBINATION (SLS)")

q_qp = calculate_line_load(
    slab_construction=slab_construction,
    loads=test_loads,
    combination="QUASI-PERMANENT")

deflection_qp = DeflectionCalculator.calculate_deflection(
    slab_construction=slab_construction,
    loads=test_loads,
    system="SIMPLE_BEAM",
    combination="QUASI-PERMANENT",
    n_intervals=40,
    n_axial=0.0,
    debug=False
)

print(f"   q_qp: {q_qp:.2f} kN/m")
print(f"   Deflection: {deflection_qp:.2f} mm")
print(f"   Deflection/Span: L/{span_m * 1000 / deflection_qp:.0f}")

# Frequent combination
print("\n3. FREQUENT COMBINATION (SLS)")

q_freq = calculate_line_load(
    slab_construction=slab_construction,
    loads=test_loads,
    combination="FREQUENT")

deflection_freq = DeflectionCalculator.calculate_deflection(
    slab_construction=slab_construction,
    loads=test_loads,
    system="SIMPLE_BEAM",
    combination="FREQUENT",
    n_intervals=40,
    n_axial=0.0,
    debug=False
)

print(f"   q_freq: {q_freq:.2f} kN/m")
print(f"   Deflection: {deflection_freq:.2f} mm")
print(f"   Deflection/Span: L/{span_m * 1000 / deflection_freq:.0f}")

# Common deflection limits
print(f"\n" + "=" * 70)
print("DEFLECTION LIMIT CHECKS (EC2)")
print("=" * 70)

limits = {
    "L/250 (appearance)": span_m * 1000 / 250,
    "L/500 (partitions)": span_m * 1000 / 500,
}

print(f"\nQuasi-permanent deflection: {deflection_qp:.2f} mm")
for limit_name, limit_value in limits.items():
    utilization = -deflection_qp / limit_value
    status = "✓ OK" if utilization <= 1.0 else "✗ FAIL"
    print(f"  {limit_name}: {limit_value:.2f} mm - "
          f"Utilization: {utilization:.2%} {status}")

print("\n" + "=" * 70)