import os

import numpy as np
from matplotlib import pyplot as plt

from _mains.testing_files import testing_loads
from _mains.testing_files.testing_hp_sections import (
    hp_section_c2_uls_x_0_00, hp_section_c2_uls_x_0_10,
    hp_section_c2_uls_x_0_20, hp_section_c2_uls_x_0_30,
    hp_section_c2_uls_x_0_40, hp_section_c2_uls_x_0_50, hp_section_c1_3_uls, hp_section_ref_x_0_50, hp_shell_ref,
)
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import test_slab_construction_ref
from core.analysis_core.section_methods import (
    calculate_moment_curvature_sls_EC,
    calculate_bending_strength_sls_Nmm_EC,
)
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces
from core.visualization_core.visualization import (
    plot_moment_curvature_with_reference,
    PlotLine, plot_moment_curvature_multiple, plot_moment_curvature_multiple_and_differences, TU_COLORS, mirror_plot,
)
plt.rcParams["font.family"] = "STIXGeneral"

"""
Author: Elliot Melcer
This file is used to compare the moment-curvature-diagrams calculated by Loutfi's 
Grasshopper script and SlabDesignBench for the reference design
"""

# Python MKD────────────────────────────────────────────────────────────────
x_position = 0.4375
slab_con = test_slab_construction_ref
section = hp_shell_ref.section_at(x_position)

# simplified
mk_ref_simpl_results = calculate_moment_curvature_sls_EC(
    section,
    simplification=0.15,
    debug = False
)
ref_moments_simpl = mk_ref_simpl_results.m_y
ref_curvatures_simpl = mk_ref_simpl_results.chi_y

# full
# mk_ref_full_results = calculate_moment_curvature_sls_EC(
#     section,
#     simplification=False
# )
# ref_moments_full = mk_ref_full_results.m_y
# ref_curvatures_full = mk_ref_full_results.chi_y

q_qp = test_loads.combined_line_load_kN_m(slab_con, "QUASI_PERMANENT")
print("q_qp = ", q_qp)

# Loutfi's MKD───────────────────────────────────────────────────────────────
LOUTFI = {
    0.0: {
        "moments": [0, 37.445, 92.85],
        "curvatures": [-0.000316e3, 0.001363e3, 0.040172e3],
    },
    0.5: {
        "moments": [0, 53.85, 144.235],
        "curvatures": [-0.000989e3, 0.001383e3, 0.034746e3],
    },
}

# if x_position == 0.0 or x_position == 0.5:
#     loutfi_moments = LOUTFI[x_position]["moments"]
#     loutfi_curvatures = LOUTFI[x_position]["curvatures"]
# else:
#     loutfi_moments_sup = LOUTFI[0.0]["moments"]
#     loutfi_curvatures_sup = LOUTFI[0.0]["curvatures"]
#     loutfi_moments_mid = LOUTFI[0.5]["moments"]
#     loutfi_curvatures_mid = LOUTFI[0.5]["curvatures"]
#
#     loutfi_moments = DeflectionCalculator._parabolic_interpolate(np.asarray(loutfi_moments_sup), np.asarray(loutfi_moments_mid), x_position)
#     loutfi_curvatures = DeflectionCalculator._parabolic_interpolate(np.asarray(loutfi_curvatures_sup), np.asarray(loutfi_curvatures_mid), x_position)

# Python kappa(x)───────────────────────────────────────────────────────────────

x_intervals = np.linspace(0, 0.5, 41)
sdb_kappa_x,_ = DeflectionCalculator._get_interpolated_kappa_array(
    slab_con,
    loads = test_loads,
    system=SystemType.SIMPLE_BEAM,
    combination="QUASI_PERMANENT",
    n_intervals=40,
    N_axial_N=0,
    constitutive_law="TENSTIFF_PARABOLIC",
    m_k_simplification=0.15
)

# Loutfi kappa(x)───────────────────────────────────────────────────────────────
loutfi_kappa_x = [-0.000316, -0.000228762, -0.000144006, -6.16949E-05, 1.82036E-05, 9.57183E-05, 0.000170875, 0.000243697, 0.000314204, 0.000382417, 0.000448351, 0.000512021, 0.000573443, 0.000632628, 0.000689588, 0.000744333, 0.000796873, 0.000847216, 0.000895371, 0.000941345, 0.000985143, 0.001026773, 0.00106624, 0.001103548, 0.001138703, 0.001171709, 0.001202569, 0.001231287, 0.001257866, 0.001282309, 0.001304618, 0.001324796, 0.001342845, 0.001358766, 0.001372562, 0.001395748, 0.001475312, 0.001536854, 0.001580632, 0.001606827, 0.001615546]


# Lines ────────────────────────────────────────────────────────────────────────
# mk_line_simpl_sdb     = PlotLine(-ref_moments_simpl / 1e6, -ref_curvatures_simpl * 1e6, name="SlabDesignBench, simplification = 0.15", color=TU_COLORS["BLACK"], linestyle="solid", marker = "o")
# mk_line_full_sdb     = PlotLine(-ref_moments_full / 1e6, -ref_curvatures_full * 1e6, name="SlabDesignBench, simplification = 0.15", color=TU_COLORS["BLACK"], linestyle="solid")

# mk_loutfi           = PlotLine(loutfi_moments, loutfi_curvatures, name="LOUTFI", color=TU_COLORS["ORANGE"], linestyle="solid")

sdb_kappas_x_line        = PlotLine(list(x_intervals),sdb_kappa_x, name="SlabDesignBench", color=TU_COLORS["BLACK"], linestyle="solid")
loutfi_kappas_x_line     = PlotLine(list(x_intervals), loutfi_kappa_x, name="Grasshopper", color=TU_COLORS["BLACK"], linestyle="dashed")

'# Plot──────────────────────────────────────────────────────────────────────────'
# FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")

# 1. M-K-diagram Comparison of Loutfi vs. SlabDesignBench simplification = 0.15
m_k_lines = [
    # mk_line_simpl_sdb,
    # mk_line_full_sdb,
    # mk_loutfi,
]

kappa_x_lines = [
    sdb_kappas_x_line,
    loutfi_kappas_x_line
]

# fig_1, ax_main1 = plot_moment_curvature_multiple(m_k_lines)
# # fig_1.savefig(os.path.join(FIGURES_DIR,"mkd_gh_vs_sdb.pdf"), bbox_inches="tight")
#
# # --- Horizontal M_qp line spanning the full x-axis ---
# # Moment under quasi-permanent-load
# load = test_loads
# line_load_qp = load.combined_line_load_kN_m(test_slab_construction_ref, "QUASI_PERMANENT")
# span = test_slab_construction_ref.slab.hp_shell.hp_geometry.L / 1000
# M_qp_kNm = InternalForces.moment_simple_beam(x_position * span, line_load_qp, span)
#
# ax_main1.axhline(
#     M_qp_kNm,
#     color=TU_COLORS["RED"],
#     linestyle="dotted",
#     linewidth=1.2,
#     label=f"M_qp = {M_qp_kNm:.1f} kNm",
#     zorder=2,
# )

mirror_plot(
    kappa_x_lines,
    xmarker=0.1,
    ymarker=0.5e-3,
    ylabel="curvatures [mm/m]",
    flip_y_axis=True,
    show_x_numbers=True,
    show_x_ticks=False,
    show_x_axis_label=True,
    x_number_pad=2.,
    x_number_position="top",
    show_legend=True,
    xlim=(0, 1.05),
    ylim=(-0.5, 1.7),
    y_scale=1000,
    figsize=(8,3),
)

plt.show()