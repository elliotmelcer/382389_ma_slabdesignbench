"""
Author: Elliot Melcer
This file is used to produce a combined plot of full and simplified MK-Diagrams
at prestress levels 0%, 10%, 20%, 30%, 40%, 50%.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from matplotlib import pyplot as plt
from structuralcodes.materials.constitutive_laws import Elastic
from structuralcodes.materials.concrete import Concrete
from structuralcodes.materials.reinforcement import create_reinforcement



from _mains.testing_files.testing_floor import test_floor
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_materials import (
    concrete_c50_uls,
    concrete_c55_uls,
    concrete_c80_uls,
    fyk_Q95,  ftk_Q95,  Es_Q95,  epsuk_Q95,  density_Q95,  brittle_elastic_law_Q95,
    fyk_Q142, ftk_Q142, Es_Q142, epsuk_Q142, density_Q142, brittle_elastic_law_Q142,
    infill,
)
from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_3
from core.analysis_core.section_methods import sls_section_EC, calculate_moment_curvature_sls_EC
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces
from core.visualization_core.visualization import plot_moment_curvature, plot_moment_curvature_multiple, PlotLine, \
    TU_COLORS
from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.hp_model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.hp_model.hp_slab import HPSlab

plt.rcParams["font.family"] = "STIXGeneral"

# ------------------------------------------------------------------------------
# Config dataclass
# ------------------------------------------------------------------------------

@dataclass
class SlabConfig:
    """
    Holds all fixed parameters for a C1_x test configuration.
    The only thing that varies across test cases is the prestress level.
    """
    name: str
    hp_geom: HPGeometry
    concrete: Concrete
    fyk: float
    ftk: float
    Es: float
    epsuk: float
    density: float
    constitutive_law: Elastic
    gamma_s: float
    reinf_name: str
    reinf_area: float  # mm²

    def build_slab_construction(self, prestress_factor: float) -> SlabConstruction:
        """
        Build a complete SlabConstruction for a given prestress factor.

        :param prestress_factor: Fraction of epsuk, e.g. 0.5 = 50%.
        :return: SlabConstruction
        """
        pct = prestress_factor * 100
        reinforcement = create_reinforcement(
            fyk=self.fyk,
            Es=self.Es,
            ftk=self.ftk,
            epsuk=self.epsuk,
            density=self.density,
            constitutive_law=self.constitutive_law,
            initial_strain=prestress_factor * self.epsuk,
            gamma_s=self.gamma_s,
            name=f"{self.reinf_name} prestressed {pct:.0f}%",
        )
        hp_shell = HPShell(self.hp_geom, self.concrete, reinforcement, reinf_area=self.reinf_area)
        hp_slab = HPSlab(hp_shell, infill)
        return SlabConstruction(hp_slab, test_floor)


# ------------------------------------------------------------------------------
# Configurations (Turn on which you want to print)
# ------------------------------------------------------------------------------

ALL_CONFIGS = [
    SlabConfig(
        name="C1_1",
        hp_geom=HPGeometry(B=1200, L=6750, Hx=40, Hy=160, t=40, dy=100, nt=7),
        concrete=concrete_c50_uls,
        fyk=fyk_Q95, ftk=ftk_Q95, Es=Es_Q95, epsuk=epsuk_Q95,
        density=density_Q95, constitutive_law=brittle_elastic_law_Q95,
        gamma_s=1.3, reinf_name="solidian GRID Q95/95-CCE-38",
        reinf_area=50,
    ),
    # SlabConfig(
    #     name="C1_2_1",
    #     hp_geom=HPGeometry(B=1200, L=6750, Hx=75, Hy=300, t=70, dy=50, nt=8),
    #     concrete=concrete_c50_uls,
    #     fyk=fyk_Q95, ftk=ftk_Q95, Es=Es_Q95, epsuk=epsuk_Q95,
    #     density=density_Q95, constitutive_law=brittle_elastic_law_Q95,
    #     gamma_s=1.3, reinf_name="solidian GRID Q95/95-CCE-38",
    #     reinf_area=50,
    # ),
    # SlabConfig(
    #     name="C1_2_2",
    #     hp_geom=HPGeometry(B=1200, L=6750, Hx=75, Hy=300, t=70, dy=50, nt=8),
    #     concrete=concrete_c80_uls,
    #     fyk=fyk_Q95, ftk=ftk_Q95, Es=Es_Q95, epsuk=epsuk_Q95,
    #     density=density_Q95, constitutive_law=brittle_elastic_law_Q95,
    #     gamma_s=1.3, reinf_name="solidian GRID Q95/95-CCE-38",
    #     reinf_area=50,
    # ),
    # SlabConfig(
    #     name="C1_3",
    #     hp_geom=HPGeometry(B=1500, L=6750, Hx=125, Hy=500, t=50, dy=50, nt=1),
    #     concrete=concrete_c50_uls,
    #     fyk=fyk_Q142, ftk=ftk_Q142, Es=Es_Q142, epsuk=epsuk_Q142,
    #     density=density_Q142, constitutive_law=brittle_elastic_law_Q142,
    #     gamma_s=1.3, reinf_name="solidian GRID Q142/142-CCE-25",
    #     reinf_area=300,
    # ),
    # SlabConfig(
    #     name="C1_4",
    #     hp_geom=HPGeometry(B=1200, L=6750, Hx=100, Hy=400, t=100, dy=80, nt=10),
    #     concrete=concrete_c55_uls,
    #     fyk=fyk_Q142, ftk=ftk_Q142, Es=Es_Q142, epsuk=epsuk_Q142,
    #     density=density_Q142, constitutive_law=brittle_elastic_law_Q142,
    #     gamma_s=1.3, reinf_name="solidian GRID Q142/142-CCE-25",
    #     reinf_area=80,
    # ),
]

# ------------------------------------------------------------------------------
# Prestress levels (Add prestress levels you want to include)
# ------------------------------------------------------------------------------
PRESTRESS_LEVELS_PCT = [0., 10., 20., 30., 40., 50.]

# ------------------------------------------------------------------------------
#  Position along beam (specify x along the beam.
#  recommended: x = 0 for support and x = 0.5 for midspan)
#  ------------------------------------------------------------------------------
x_position = 0.0625

# ------------------------------------------------------------------------------
# Run and plot
# ------------------------------------------------------------------------------

def _grey_shade(i: int, n: int, max_value: int = 160) -> str:
    """
    Returns a hex grey color: i=0 -> black, i=n-1 -> light grey.
    max_value caps how light the lightest shade gets (255 = white).
    160 keeps the lightest line still clearly visible on a white background.
    """
    v = int(round(i / (n - 1) * max_value)) if n > 1 else 0
    return f"#{v:02x}{v:02x}{v:02x}"


for config in ALL_CONFIGS:
    line_list = []


    for i, pct in enumerate(PRESTRESS_LEVELS_PCT):
        color = _grey_shade(i, len(PRESTRESS_LEVELS_PCT))

        slab_construction = config.build_slab_construction(pct / 100)

        midspan_section = slab_construction.slab.section_at(x_position)

        mkd_full = calculate_moment_curvature_sls_EC(midspan_section, simplification=False)
        mkd_simp = calculate_moment_curvature_sls_EC(midspan_section, simplification=True)

        line_list.append(PlotLine(
            -mkd_full.m_y / 1e6,
            -mkd_full.chi_y * 1000,
            name=f"Full {pct:.0f}%",
            color=color,
            linestyle="solid",
        ))
        line_list.append(PlotLine(
            -mkd_simp.m_y / 1e6,
            -mkd_simp.chi_y * 1000,
            name=f"Simplified {pct:.0f}%",
            color=color,
            linestyle="dashed",
        ))

    # Moment under quasi-permanent-load
    load = test_loads
    line_load_qp = load.combined_line_load_kN_m(test_slab_construction_c1_3, "QUASI_PERMANENT")
    span = config.hp_geom.L/1000
    M_qp_kNm = InternalForces.moment_simple_beam(x_position*span, line_load_qp, span)

    if x_position == 0.0:
        x_title = "support"
    elif x_position == 0.5:
        x_title = "midspan"
    else:
        x_title = f" x_norm = {x_position:.3f}"

    fig, ax = plot_moment_curvature_multiple(
        line_list,
        title=f"M-K-Diagrams at {x_title} of {config.name} — full vs. simplified, varying prestress",
        ymarker=50,
    )

    # --- Horizontal M_qp line spanning the full x-axis ---
    ax.axhline(
        M_qp_kNm,
        color=TU_COLORS["RED"],
        linestyle="dotted",
        linewidth=1.2,
        label=f"M_qp = {M_qp_kNm:.1f} kNm",
        zorder=2,
    )
    ax.legend(loc="lower right")  # refresh legend to include the new line

    FIGURES_DIR = Path(__file__).resolve().parent / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if x_position == 0.0:
        x_text = "_sup"
    elif x_position == 0.5:
        x_text = "_mid"
    else:
        x_text = f"_{x_position:.2f}".replace(".", "_")
    fig.savefig(os.path.join(FIGURES_DIR, f"mkd_{config.name}{x_text}_by_pre_lvl_full_and_simp.pdf"), bbox_inches="tight")

plt.show()
