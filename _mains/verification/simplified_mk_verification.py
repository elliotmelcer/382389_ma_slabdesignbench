import os

from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_4_uls
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_3, test_slab_construction_c1_4
from core.analysis_core.section_methods import calculate_moment_curvature_sls_EC
from core.visualization_core.visualization import plot_moment_curvature, plot_moment_curvature_multiple, \
    PlotLine, TU_COLORS

"""
This File is used to show how the moment-curvature-diagram changes when additional points are introduced using the 
input parameter 'simplification' for calculate_moment_curvature_sls_EC()-function.  
"""

# ╭┬╮   ╷╭   ╶┬╮╷╭-╮╭-╴╭-╮╭-╮╭┬╮
# |||╶-╴├┴╮╶-╴|||├-┤|╶╮├┬╯├-┤|||
# ╵ ╵   ╵ ╵  ╶┴╯╵╵ ╵╰-╯╵╰╴╵ ╵╵ ╵
section = hp_section_c1_4_uls

print("Calculating moment-curvature: FULL (simplification=False)...")
mk_results_full = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=False,
    debug=False
)

print("Calculating moment-curvature: SIMPLIFIED (simplification=True)...")
mk_results_simplified = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=True,
    debug=False
)

print("Calculating moment-curvature: AUG 1 (simplification=1)...")
mk_results_aug_1 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=1,
    debug=False
)

print("Calculating moment-curvature: AUG 2 (simplification=2)...")
mk_results_aug_2 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=2,
    debug=False
)

print("Calculating moment-curvature: AUG 3 (simplification=3)...")
mk_results_aug_3 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=3,
    debug=False
)

print("Calculating moment-curvature: AUG 0.25 (simplification=0.25)...")
mk_results_aug_0_25 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=0.25,
    debug=False
)

print("Calculating moment-curvature: AUG 0.50 (simplification=0.50)...")
mk_results_aug_0_50 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=0.50,
    debug=False
)

print("Calculating moment-curvature: AUG 0.75 (simplification=0.75)...")
mk_results_aug_0_75 = calculate_moment_curvature_sls_EC(
    section,
    n=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    simplification=0.75,
    debug=False
)

# ╷  ╷╭╮╷╭-╴╭-╮
# |  ||╰┤├╴ ╰-╮
# ╰-╴╵╵ ╵╰-╴╰-╯

print("Creating PlotLine: FULL...")
mk_line_full       = PlotLine.from_results(mk_results_full, name="FULL", color=TU_COLORS["BLACK"], linestyle="solid")
print("Creating PlotLine: SIMPLIFIED...")
mk_line_simplified = PlotLine.from_results(mk_results_simplified, name="SIMPLIFIED", color=TU_COLORS["RED"], linestyle="solid", marker ="o")

print("Creating PlotLine: AUG 1...")
mk_line_aug_1      = PlotLine.from_results(mk_results_aug_1, name="AUG 1", color=TU_COLORS["ORANGE"], linestyle="dashdot", marker ="o")
print("Creating PlotLine: AUG 2...")
mk_line_aug_2      = PlotLine.from_results(mk_results_aug_2, name="AUG 2", color=TU_COLORS["VIOLET"], linestyle="dashdot", marker ="^")
print("Creating PlotLine: AUG 3...")
mk_line_aug_3      = PlotLine.from_results(mk_results_aug_3, name="AUG 3", color=TU_COLORS["GREEN"], linestyle="dashdot", marker ="s")
print("Creating PlotLine: AUG 0.25...")

mk_line_aug_0_25   = PlotLine.from_results(mk_results_aug_0_25, name="AUG 0.25", color=TU_COLORS["ORANGE"], linestyle="dashed", marker ="o")
print("Creating PlotLine: AUG 0.50...")
mk_line_aug_0_50   = PlotLine.from_results(mk_results_aug_0_50, name="AUG 0.50", color=TU_COLORS["VIOLET"], linestyle="dashed", marker ="^")
print("Creating PlotLine: AUG 0.75...")
mk_line_aug_0_75   = PlotLine.from_results(mk_results_aug_0_75, name="AUG 0.75", color=TU_COLORS["GREEN"], linestyle="dotted", marker ="s")

# ╷  ╷╭-╮╶┬╴╭-╮
# |  |╰-╮ | ╰-╮
# ╰-╴╵╰-╯ ╵ ╰-╯

list_full_simplified = [
    mk_line_simplified,
    mk_line_full,
]

list_full_aug_int_1 = [
    mk_line_aug_1,
    mk_line_full,
]

list_full_aug_int_2 = [
    mk_line_aug_2,
    mk_line_full,
]

list_full_aug_int_3 = [
    mk_line_aug_3,
    mk_line_full,
]

list_full_aug_float_0_25 = [
    mk_line_aug_0_25,
    mk_line_full,
]

list_full_aug_float_0_50 = [
    mk_line_aug_0_50,
    mk_line_full,
]

list_full_aug_float_0_75 = [
    mk_line_aug_0_75,
    mk_line_full,
]


# ╭-╮╷  ╭-╮╶┬╴  ╭-╮╭-╴╶┬╴╶┬╴╷╭╮╷╭-╴╭-╮
# ├-╯|  | | |   ╰-╮├╴  |  | ||╰┤|╶╮╰-╮
# ╵  ╰-╴╰-╯ ╵   ╰-╯╰-╴ ╵  ╵ ╵╵ ╵╰-╯╰-╯

FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")
x_lim = (1.8, 6.4)
y_lim = (390, 610)

# ╭-╴╷ ╷╷  ╷    ╷ ╷╭-╮  ╭-╮╷╭┬╮╭-╮╷  ╷╭-╴╷╭-╴╶┬╮
# ├╴ | ||  |    |╭╯╰-╮  ╰-╮||||├-╯|  |├╴ |├╴  ||
# ╵  ╰-╯╰-╴╰-╴  ╰╯ ╰-╯  ╰-╯╵╵ ╵╵  ╰-╴╵╵  ╵╰-╴╶┴╯

print("Plotting: full vs simplified...")
fig_full_simplified, ax_fs = plot_moment_curvature_multiple(list_full_simplified, ymarker=50.)
# fig_full_simplified.savefig(os.path.join(FIGURES_DIR, "simp_full_simplified.pdf"), bbox_inches="tight")

# ╷╭╮╷╶┬╴╭-╴╭-╴╭-╴╭-╮
# ||╰┤ | ├╴ |╶╮├╴ ├┬╯
# ╵╵ ╵ ╵ ╰-╴╰-╯╰-╴╵╰╴

print("Plotting: full vs AUG 1...")
fig_full_aug_int_1, ax_ai1 = plot_moment_curvature_multiple(list_full_aug_int_1, ymarker=50.)
# fig_full_aug_int_1.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_int_1.pdf"), bbox_inches="tight")

print("Plotting: full vs AUG 2...")
fig_full_aug_int_2, ax_ai2 = plot_moment_curvature_multiple(list_full_aug_int_2, ymarker=50.)
# fig_full_aug_int_2.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_int_2.pdf"), bbox_inches="tight")

print("Plotting: full vs AUG 3...")
fig_full_aug_int_3, ax_ai3 = plot_moment_curvature_multiple(list_full_aug_int_3, ymarker=50.)
# fig_full_aug_int_3.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_int_3.pdf"), bbox_inches="tight")

# ╭-╴╷  ╭-╮╭-╮╶┬╴
# ├╴ |  | |├-┤ |
# ╵  ╰-╴╰-╯╵ ╵ ╵

# print("Plotting: full vs AUG 0.25...")
fig_full_aug_float_0_25, ax_af025 = plot_moment_curvature_multiple(list_full_aug_float_0_25, ymarker=50.)
# fig_full_aug_float_0_25.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_float_0_25.pdf"), bbox_inches="tight")

print("Plotting: full vs AUG 0.50...")
fig_full_aug_float_0_50, ax_af050 = plot_moment_curvature_multiple(list_full_aug_float_0_50, ymarker=50.)
# fig_full_aug_float_0_50.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_float_0_50.pdf"), bbox_inches="tight")

print("Plotting: full vs AUG 0.75...")
fig_full_aug_float_0_75, ax_af075 = plot_moment_curvature_multiple(list_full_aug_float_0_75, ymarker=50.)
# fig_full_aug_float_0_75.savefig(os.path.join(FIGURES_DIR, "simp_full_aug_float_0_75.pdf"), bbox_inches="tight")

plt.show()