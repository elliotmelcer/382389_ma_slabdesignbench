import os
from matplotlib import pyplot as plt
from _mains.testing_files.testing_materials import concrete_c30_uls, solidian_Q142, reinforcement_B500
from core.analysis_core.material_methods import create_sls_concrete_EC
from core.visualization_core.visualization import plot_constitutive_law_concrete, plot_constitutive_law_reinforcement

plt.rcParams["font.family"] = "STIXGeneral"

# Set Up Materials ─────────────────────────────────────────────────────────────
# Concrete
c_30 = concrete_c30_uls

c_30_np = create_sls_concrete_EC(c_30, "NONE_PARABOLIC")
c_30_fp = create_sls_concrete_EC(c_30, "FCTM_PARABOLIC")
c_30_tp = create_sls_concrete_EC(c_30, "TENSTIFF_PARABOLIC")
c_30_ee = create_sls_concrete_EC(c_30, "ELASTIC_ELASTIC")

# Reinforcement
reinf_cfk_q142 = solidian_Q142

# Plot──────────────────────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "figures")

# Concrete
fig_claw_uls, ax1_uls = plot_constitutive_law_concrete(c_30)
fig_claw_uls.savefig(os.path.join(FIGURES_DIR,"claw_c30_uls.pdf"), bbox_inches="tight")

fig_claw_np, ax1_np = plot_constitutive_law_concrete(c_30_np)
fig_claw_np.savefig(os.path.join(FIGURES_DIR,"claw_c30_np.pdf"), bbox_inches="tight")

fig_claw_fp, ax1_fp = plot_constitutive_law_concrete(c_30_fp)
fig_claw_fp.savefig(os.path.join(FIGURES_DIR,"claw_c30_fp.pdf"), bbox_inches="tight")

fig_claw_tp, ax1_tp = plot_constitutive_law_concrete(c_30_tp)
fig_claw_tp.savefig(os.path.join(FIGURES_DIR,"claw_c30_tp.pdf"), bbox_inches="tight")

fig_claw_ee, ax1_ee = plot_constitutive_law_concrete(c_30_ee)
fig_claw_ee.savefig(os.path.join(FIGURES_DIR,"claw_c30_ee.pdf"), bbox_inches="tight")

# Reinforcement
fig_claw_soli, ax1_soli = plot_constitutive_law_reinforcement(reinf_cfk_q142)
fig_claw_soli.savefig(os.path.join(FIGURES_DIR,"claw_soli.pdf"), bbox_inches="tight")

plt.show()
