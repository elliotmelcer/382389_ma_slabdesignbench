import os

from matplotlib import pyplot as plt
from _mains.testing_files.testing_hp_sections import (
    hp_section_c2_uls_x_0_00, hp_section_c2_uls_x_0_10,
    hp_section_c2_uls_x_0_20, hp_section_c2_uls_x_0_30,
    hp_section_c2_uls_x_0_40, hp_section_c2_uls_x_0_50, hp_section_c1_3_uls,
)
from core.analysis_core.section_methods import (
    calculate_moment_curvature_sls_EC,
    calculate_bending_strength_sls_Nmm_EC,
)
from core.visualization_core.visualization import (
    plot_moment_curvature_with_reference,
    PlotLine, plot_moment_curvature_multiple, plot_moment_curvature_multiple_and_differences, TU_COLORS,
)
plt.rcParams["font.family"] = "STIXGeneral"


"""
Author: Elliot Melcer
This file is used to compare the moment-curvature-diagrams calculated by INCA2 and SlabDesignBench 
for multiple positions along the beam C.2 using local variable LOCATION
"""

# ── INCA reference data (M in kNm, curvature in mm/m)─────────────────────────
# SETTINGS:  NAME OF CONCRETE MATERIAL
#   Zug:  Spannung bei Erreichen der Fließgrenze [N/mm²], Dehnung bei Erreichen der Fließgrenze [mm/m], Exponent k
#   MBZ*: eps_cr, eps_u, n

# *Mitwirkung des Betons auf Zug

# Data ──────────────────────────────────────────────────────────────────────────
# modified: only positive moment values
INCA_NONE_PARA = {
    0.00: {
        "curvatures": [-0.0264, 0.0000, 0.2824, 0.4707, 0.5649, 0.6590, 0.7531, 0.8473, 0.9414, 1.0356, 1.1297, 1.2238, 1.3180, 1.5063, 1.6946, 1.9770, 2.2594, 2.6360, 3.1067, 3.7657, 4.6130, 5.8368, 7.6255, 10.4498, 15.0627, 18.8284],
        "moments":    [0.0000, 0.4146, 4.8491, 7.7987, 9.2502, 10.5127, 11.5180, 12.3067, 12.9614, 13.5213, 14.0097, 14.4426, 14.8315, 15.5062, 16.0785, 16.8031, 17.4152, 18.1129, 18.8570, 19.7480, 20.7354, 21.9819, 23.6005, 25.9200, 29.4393, 32.1932]
    },
    0.10: {
        "curvatures": [-0.2365, -0.2194, 0.0000, 0.4744, 0.5693, 0.6642, 0.7591, 0.8539, 0.9488, 1.0437, 1.1386, 1.2335, 1.4232, 1.6130, 1.8976, 2.1823, 2.5618, 3.1311, 3.8902, 4.9339, 6.4520, 8.8240, 12.7142, 18.9764],
        "moments":    [0.0000, 0.2681, 3.7127, 11.1365, 12.5925, 13.8530, 14.8551, 15.6428, 16.2985, 16.8611, 17.3532, 17.7903, 18.5406, 19.1703, 19.9611, 20.6270, 21.3849, 22.3427, 23.4196, 24.6920, 26.3173, 28.6007, 32.0556, 37.3115]
    },
    0.20: {
        "curvatures": [-0.4116, -0.2829, 0.0000, 0.4793, 0.5752, 0.6710, 0.7669, 0.8627, 0.9586, 1.0544, 1.1503, 1.2462, 1.4379, 1.6296, 1.9172, 2.3006, 2.7799, 3.4509, 4.4095, 5.7515, 7.8604, 11.4072, 17.4462, 19.1717],
        "moments":    [0.0000, 1.8398, 6.2779, 13.7713, 15.2356, 16.4946, 17.4910, 18.2779, 18.9351, 19.4999, 19.9951, 20.4358, 21.1959, 21.8375, 22.6485, 23.5439, 24.4772, 25.5778, 26.9174, 28.5549, 30.8594, 34.4201, 40.1272, 41.7129]
    },
    0.30: {
        "curvatures": [-0.6406, -0.5660, -0.3774, -0.1887, 0.0000, 0.4785, 0.5742, 0.6699, 0.7656, 0.8613, 0.9570, 1.0527, 1.1484, 1.3398, 1.5312, 1.8184, 2.2012, 2.6797, 3.3496, 4.3066, 5.7422, 8.0390, 11.9628, 18.5663, 19.1405],
        "moments":    [0.0000, 0.4070, 2.2319, 5.1511, 8.1102, 15.5907, 17.0543, 18.3160, 19.3179, 20.1097, 20.7714, 21.3413, 21.8420, 22.6916, 23.3980, 24.2802, 25.2442, 26.2439, 27.4194, 28.8497, 30.7184, 33.3954, 37.6125, 44.3220, 44.8920]
    },
    0.40: {
        "curvatures": [-0.8963, -0.7906, -0.5271, -0.2635, 0.0000, 0.4855, 0.5826, 0.6796, 0.7767, 0.8738, 0.9709, 1.0680, 1.1651, 1.3593, 1.5535, 1.8448, 2.2331, 2.7186, 3.3982, 4.3692, 5.8255, 8.2529, 12.4278, 19.4185],
        "moments":    [0.0000, 0.3320, 1.7939, 5.0743, 9.2095, 16.7997, 18.2753, 19.5333, 20.5240, 21.3105, 21.9706, 22.5400, 23.0409, 23.8930, 24.6044, 25.4973, 26.4786, 27.5013, 28.7122, 30.1968, 32.1518, 35.0854, 39.7582, 47.1776]
    },
    0.50: {
        "curvatures": [-1.0164, -0.8372, -0.5582, -0.2791, 0.0000, 0.4799, 0.5759, 0.6718, 0.7678, 0.8638, 0.9598, 1.0557, 1.1517, 1.3437, 1.5356, 1.8235, 2.2074, 2.6873, 3.3591, 4.3189, 5.7585, 8.1579, 12.2848, 19.1950],
        "moments":    [0.0000, 0.5094, 1.9111, 5.1723, 9.5585, 17.0731, 18.5417, 19.8061, 20.8094, 21.6037, 22.2690, 22.8427, 23.3473, 24.2058, 24.9220, 25.8203, 26.8074, 27.8360, 29.0537, 30.5468, 32.5127, 35.4626, 40.1615, 47.6239]
    },
}

# ── Section objects, keyed by the same positions ──────────────────────────────
SECTIONS = {
    0.00: hp_section_c2_uls_x_0_00,
    0.10: hp_section_c2_uls_x_0_10,
    0.20: hp_section_c2_uls_x_0_20,
    0.30: hp_section_c2_uls_x_0_30,
    0.40: hp_section_c2_uls_x_0_40,
    0.50: hp_section_c2_uls_x_0_50,
}


" ── Run ───────────────────────────────────────────────────────────────────────"
"Set Location here:"

" ──────────────────────────────────────────────────────────────────────────────"

lines_inca_python_comparison = []

for LOCATION in [0.00, 0.10, 0.20, 0.30, 0.40, 0.50]:

    inca_np = INCA_NONE_PARA[LOCATION]
    inca_np_moments = inca_np["moments"]
    inca_np_curvatures = inca_np["curvatures"]


    # Python Results────────────────────────────────────────────────────────────────
    section     = SECTIONS[LOCATION]

    # Python Results────────────────────────────────────────────────────────────────
    section = SECTIONS[LOCATION]

    mk_np_results = calculate_moment_curvature_sls_EC(section, constitutive_law="NONE-PARABOLIC")

    mk_line_inca_np = PlotLine(
        inca_np_moments,
        inca_np_curvatures,
        name="INCA_NONE-PARA",
        color=TU_COLORS["BLUE"],
        linestyle="solid"
    )
    mk_line_np_python_o = PlotLine.from_results(
        mk_np_results,
        name="Python_NONE-PARA",
        color=TU_COLORS["ORANGE"],
        linestyle="solid"
    )

    lines_inca_python_comparison.append(mk_line_inca_np)
    lines_inca_python_comparison.append(mk_line_np_python_o)

# Plot Settings─────────────────────────────────────────────────────────────────
# Axis Extents
zoom_x = (-5.,20.)
zoom_y = (-5.,50.)


'# Plot──────────────────────────────────────────────────────────────────────────'
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")

# Comparison of Python and INCA2 M-K-diagrams for NONE_PARABOLIC
fig_3, ax_3 = plot_moment_curvature_multiple(lines_inca_python_comparison, title="C.2 Comparison of INCA2 and Python with NONE_PARABOLIC constitutive law", x=LOCATION, xlim = zoom_x, ylim = zoom_y)
# fig_3.savefig(os.path.join(FIGURES_DIR,"comp_inca_python.pdf"), bbox_inches="tight")


plt.show()