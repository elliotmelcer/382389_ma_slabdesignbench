import os
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from core.visualization_core.visualization import TU_COLORS

"""
Author: Elliot Melcer
This file is used to produce a bar plot showing the difference in deflection between using simplified and full
m-k-diagram at different prestress levels. Includes data for designs C.1_1 - C.1_4 from testing_files

"""

visualize_mkd_by_pre_lvl_data = {
    "C1_1": [
        {"prestress": 0,  "simplified": 61.875, "full": 62.305, "diff": -0.430},
        {"prestress": 10, "simplified": 19.050, "full": 16.756, "diff":  2.294},
        {"prestress": 20, "simplified":  8.235, "full":  8.117, "diff":  0.118},
        {"prestress": 30, "simplified": -0.439, "full": -0.303, "diff": -0.136},
        {"prestress": 40, "simplified": -9.781, "full": -9.625, "diff": -0.156},
        {"prestress": 50, "simplified": -20.059, "full": -19.878, "diff": -0.181},
    ],

    "C1_2_C50": [
        {"prestress": 0,  "simplified": 10.768, "full":  6.443, "diff":  4.325},
        {"prestress": 10, "simplified":  2.694, "full":  2.694, "diff":  0.000},
        {"prestress": 20, "simplified": -0.013, "full":  0.096, "diff": -0.109},
        {"prestress": 30, "simplified": -2.794, "full": -2.714, "diff": -0.080},
        {"prestress": 40, "simplified": -5.676, "full": -5.612, "diff": -0.064},
        {"prestress": 50, "simplified": -8.679, "full": -8.624, "diff": -0.055},
    ],

    "C1_2_C80": [
        {"prestress": 0,  "simplified":  7.532, "full":  5.056, "diff":  2.476},
        {"prestress": 10, "simplified":  2.347, "full":  2.357, "diff": -0.010},
        {"prestress": 20, "simplified": -0.038, "full":  0.070, "diff": -0.108},
        {"prestress": 30, "simplified": -2.435, "full": -2.359, "diff": -0.076},
        {"prestress": 40, "simplified": -4.857, "full": -4.799, "diff": -0.058},
        {"prestress": 50, "simplified": -7.311, "full": -7.264, "diff": -0.047},
    ],

    "C1_3": [
        {"prestress": 0,  "simplified":  5.103, "full":  3.603, "diff":  1.500},
        {"prestress": 10, "simplified":  1.682, "full":  1.713, "diff": -0.031},
        {"prestress": 20, "simplified":  0.301, "full":  0.385, "diff": -0.084},
        {"prestress": 30, "simplified": -1.097, "full": -1.017, "diff": -0.080},
        {"prestress": 40, "simplified": -2.519, "full": -2.460, "diff": -0.059},
        {"prestress": 50, "simplified": -3.970, "full": -3.923, "diff": -0.047},
    ],

    "C1_4": [
        {"prestress": 0,  "simplified":  2.367, "full":  2.366, "diff":  0.001},
        {"prestress": 10, "simplified":  0.184, "full":  0.280, "diff": -0.096},
        {"prestress": 20, "simplified": -2.017, "full": -1.957, "diff": -0.060},
        {"prestress": 30, "simplified": -4.271, "full": -4.231, "diff": -0.040},
        {"prestress": 40, "simplified": -6.593, "full": -6.562, "diff": -0.031},
        {"prestress": 50, "simplified": -8.996, "full": -8.969, "diff": -0.027},
    ],
}

# ----------------------------------------------------------------------------------
# Plot
# ----------------------------------------------------------------------------------
# Set Font:
plt.rcParams["font.family"] = "STIXGeneral"

# Set Path
FIGURES_DIR = Path(__file__).resolve().parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

configs = list(visualize_mkd_by_pre_lvl_data.keys())
prestress_levels = [0, 10, 20, 30, 40, 50]

x = np.arange(len(prestress_levels))
bar_width = 0.15

fig, ax = plt.subplots(figsize=(7, 3))

bar_colors = [
    TU_COLORS["RED"],
    TU_COLORS["ORANGE"],
    TU_COLORS["VIOLET"],
    TU_COLORS["BLUE"],
    TU_COLORS["GREEN"],
]

for i, config in enumerate(configs):
    diffs = [
        next(row["diff"] for row in visualize_mkd_by_pre_lvl_data[config]
             if row["prestress"] == prestress)
        for prestress in prestress_levels
    ]

    ax.bar(
        x + (i - len(configs) / 2) * bar_width + bar_width / 2,
        diffs,
        width=bar_width,
        label=config,
        color=bar_colors[i],
        edgecolor=TU_COLORS["BLACK"],
        linewidth=0.0,
    )

ax.axhline(0, color=TU_COLORS["BLACK"], linewidth=0.8)
ax.grid(axis="y", linestyle="--", alpha=0.4, color=TU_COLORS["LIGHT GREY"])

ax.axhline(0, color=TU_COLORS["BLACK"], linewidth=0.8)
ax.set_xlabel("Prestress [%]")
ax.set_ylabel("Difference [mm]")
ax.set_title("Difference in Deflection between Using Simplified and Full M-κ Diagram by Prestress Level")
ax.set_xticks(x)
ax.set_xticklabels(prestress_levels)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(title="Configuration")


fig.tight_layout()

fig.savefig(os.path.join(FIGURES_DIR, f"mkd_diff_by_prestress.pdf"), bbox_inches="tight")
plt.show()