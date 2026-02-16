# For SIMPLE_BEAM - both methods work:
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from core.analysis_core.statics.internal_forces import InternalForces

x=0.25

M_at_quarter = InternalForces.calculate_moment(
    test_slab_construction_c1_4, test_loads,
    system="SIMPLE_BEAM",
    x=x  # At quarter span
)

M_max = InternalForces.calculate_moment(
    test_slab_construction_c1_4, test_loads,
    system="SIMPLE_BEAM",
    moment_type="MAX_POS_MOMENT"  # Uses coefficient
)

# For THREE_SPAN - only coefficient method works:
M_max_three_span = InternalForces.calculate_moment(
    test_slab_construction_c1_4,
    test_loads,
    system="THREE_SPAN",
    moment_type="MAX_POS_MOMENT"  # ✓ Works!
)

print(f"M(x={x}) = {M_at_quarter:.2f}")
print(f"M_max = {M_max:.2f}")
print(f"M_max_three_span = {M_max_three_span:.2f}")

# # This would raise NotImplementedError:
# M_at_pos = InternalForces.calculate_moment(
#     test_slab_construction_c1_4, test_loads,
#     system="THREE_SPAN",
#     x=0.5  # ✗ M(x) function not implemented
# )