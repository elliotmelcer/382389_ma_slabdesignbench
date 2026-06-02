# For SIMPLE_BEAM - both methods work:
import numpy as np
from matplotlib import pyplot as plt

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from core.analysis_core.statics.constants import SystemType, MomentType
from core.analysis_core.statics.internal_forces import InternalForces
from core.visualization_core.visualization import PlotLine, plot_moment_curvature_multiple

x=0.25

M_at_quarter = InternalForces.calculate_moment_kNm(
    test_slab_construction_c1_4, test_loads,
    system=SystemType.SIMPLE_BEAM,
    x_norm=x  # At quarter span
)

M_max = InternalForces.calculate_moment_kNm(
    test_slab_construction_c1_4, test_loads,
    system=SystemType.SIMPLE_BEAM,
    moment=MomentType.MAX_POS_MOMENT  # Uses coefficient
)

# For THREE_SPAN - only coefficient method works:
M_max_three_span = InternalForces.calculate_moment_kNm(
    test_slab_construction_c1_4,
    test_loads,
    system=SystemType.THREE_SPAN,
    moment=MomentType.MAX_POS_MOMENT  # ✓ Works!
)

# For TWO_SPAN:
xs = np.linspace(0, 2, 101)
m_two_span_list = []
for x in xs:
    M_max_mid_support = InternalForces.calculate_moment_kNm(
        test_slab_construction_c1_4,
        test_loads,
        system=SystemType.TWO_SPAN,
        x_norm=x
    )
    m_two_span_list.append(M_max_mid_support)

M_Line = [PlotLine(m_two_span_list, xs.tolist(), color='red', linestyle='dashed', name = "M")]

plot_moment_curvature_multiple(M_Line)

plt.show()

print(f"M(x={x}) = {M_at_quarter:.2f}")
print(f"M_max = {M_max:.2f}")
print(f"M_max_three_span = {M_max_three_span:.2f}")
print(f"M_max_mid_support = {M_max_mid_support:.2f}")

# # This would raise NotImplementedError:
# M_at_pos = InternalForces.calculate_moment(
#     test_slab_construction_c1_4, test_loads,
#     system=SystemType.THREE_SPAN,
#     x=0.5  # ✗ M(x) function not implemented
# )