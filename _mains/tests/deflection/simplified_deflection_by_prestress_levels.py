"""
Author: Elliot Melcer
Testing the difference between simplified and full moment-curvature-calculations for sections C1_1 to C1_4
under different prestress levels.

Deflection calculation parameters
    loads=                  test_loads,
    system=                 SystemType.SIMPLE_BEAM,
    combination=            "QUASI_PERMANENT",
    n_intervals=            40,
    N_axial_N=              0.0,
    constitutive_law=       "TENSTIFF_PARABOLIC",
    load_history_method=    "NONE",

Note: Running this file may take 30 minutes!

Results (DATE=?):

C1_1 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0          61.875          62.292           0.418            0.67
             10          19.050          16.764          -2.286          -13.64
             20           8.249           8.109          -0.140           -1.73
             30          -0.379          -0.410          -0.031            7.60
             40          -9.631          -9.713          -0.081            0.84
             50         -19.763         -19.949          -0.186            0.93
-------------------------------------------------------------------------------
Largest  diff : 10% prestress → -2.286 mm  (-13.64%)
Smallest diff : 30% prestress → -0.031 mm  (+7.60%)

C1_2 (C50) — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0          10.768           6.418          -4.350          -67.78
             10           2.694           2.662          -0.032           -1.21
             20          -0.011          -0.013          -0.002           12.89
             30          -2.787          -2.791          -0.004            0.15
             40          -5.659          -5.670          -0.011            0.19
             50          -8.648          -8.671          -0.023            0.27
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -4.350 mm  (-67.78%)
Smallest diff : 20% prestress → -0.002 mm  (+12.89%)

C1_2 (C80) — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           7.532           5.215          -2.317          -44.42
             10           2.347           2.326          -0.021           -0.90
             20          -0.037          -0.039          -0.001            3.32
             30          -2.433          -2.434          -0.002            0.07
             40          -4.852          -4.856          -0.003            0.07
             50          -7.303          -7.310          -0.006            0.09
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -2.317 mm  (-44.42%)
Smallest diff : 20% prestress → -0.001 mm  (+3.32%)

C1_3 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           5.103           3.518          -1.585          -45.05
             10           1.682           1.665          -0.018           -1.05
             20           0.301           0.291          -0.011           -3.64
             30          -1.096          -1.102          -0.006            0.58
             40          -2.516          -2.523          -0.007            0.29
             50          -3.964          -3.973          -0.009            0.24
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -1.585 mm  (-45.05%)
Smallest diff : 30% prestress → -0.006 mm  (+0.58%)

C1_4 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           2.367           2.418           0.051            2.10
             10           0.184           0.179          -0.005           -3.04
             20          -2.015          -2.019          -0.004            0.21
             30          -4.264          -4.272          -0.008            0.19
             40          -6.577          -6.593          -0.016            0.24
             50          -8.967          -8.994          -0.027            0.30
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → +0.051 mm  (+2.10%)
Smallest diff : 20% prestress → -0.004 mm  (+0.21%)




# ============================================================================================================

  _   _  _____ __        __    ____     _   _____   _
 │ ╲ │ ││ ____│╲ ╲      ╱ ╱   │  _ ╲   ╱ ╲ │_   _│ ╱ ╲
 │  ╲│ ││  _│   ╲ ╲ ╱╲ ╱ ╱    │ │ │ │ ╱ _ ╲  │ │  ╱ _ ╲
 │ │╲  ││ │___   ╲ V  V ╱     │ │_│ │╱ ___ ╲ │ │ ╱ ___ ╲
 │_│ ╲_││_____│   ╲_╱╲_╱      │____╱╱_╱   ╲_╲│_│╱_╱   ╲_╲

24.05.26
# ============================================================================================================

C:\Users\LJ\iCloudDrive\Documents\Studium\Master\Masterarbeit\Programmierung\382389_ma_benchmarking_suite_hp_shell\.venv\Scripts\python.exe C:\Users\LJ\iCloudDrive\Documents\Studium\Master\Masterarbeit\Programmierung\382389_ma_benchmarking_suite_hp_shell\_mains\tests\deflection\simplified_deflection_by_prestress_levels.py

C1_1 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0          61.875          62.305           0.431            0.69
             10          19.050          16.756          -2.294          -13.69
             20           8.235           8.117          -0.118           -1.45
             30          -0.439          -0.303           0.136          -44.91
             40          -9.781          -9.625           0.156           -1.62
             50         -20.059         -19.878           0.181           -0.91
-------------------------------------------------------------------------------
Largest  diff : 10% prestress → -2.294 mm  (-13.69%)
Smallest diff : 20% prestress → -0.118 mm  (-1.45%)

C1_2 (C50) — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0          10.768           6.443          -4.325          -67.12
             10           2.694           2.694           0.000            0.01
             20          -0.013           0.096           0.109          113.89
             30          -2.794          -2.714           0.080           -2.96
             40          -5.676          -5.612           0.063           -1.13
             50          -8.679          -8.624           0.055           -0.64
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -4.325 mm  (-67.12%)
Smallest diff : 10% prestress → +0.000 mm  (+0.01%)

C1_2 (C80) — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           7.532           5.056          -2.475          -48.95
             10           2.347           2.357           0.010            0.42
             20          -0.038           0.070           0.108          154.09
             30          -2.435          -2.359           0.076           -3.22
             40          -4.857          -4.799           0.058           -1.20
             50          -7.311          -7.264           0.047           -0.65
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -2.475 mm  (-48.95%)
Smallest diff : 10% prestress → +0.010 mm  (+0.42%)

C1_3 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           5.103           3.603          -1.500          -41.64
             10           1.682           1.713           0.031            1.79
             20           0.301           0.385           0.084           21.92
             30          -1.097          -1.017           0.080           -7.84
             40          -2.519          -2.460           0.059           -2.40
             50          -3.970          -3.923           0.047           -1.20
-------------------------------------------------------------------------------
Largest  diff :  0% prestress → -1.500 mm  (-41.64%)
Smallest diff : 10% prestress → +0.031 mm  (+1.79%)

C1_4 — Deflection (QP): simplification vs full MK
-------------------------------------------------------------------------------
  Prestress [%] Simplified [mm]       Full [mm]       Diff [mm]        Diff [%]
-------------------------------------------------------------------------------
              0           2.367           2.366          -0.001           -0.03
             10           0.184           0.280           0.096           34.22
             20          -2.017          -1.957           0.060           -3.08
             30          -4.271          -4.231           0.040           -0.96
             40          -6.593          -6.562           0.031           -0.48
             50          -8.996          -8.969           0.026           -0.29
-------------------------------------------------------------------------------
Largest  diff : 10% prestress → +0.096 mm  (+34.22%)
Smallest diff :  0% prestress → -0.001 mm  (-0.03%)

Process finished with exit code 0

"""
from core.analysis_core.statics.constants import SystemType

"""
Author: Elliot Melcer
Test: Deflection comparison (simplification vs full MK) across all C1_x configurations
      and prestress levels 0%, 10%, 20%, 30%, 40%, 50%.
"""

from dataclasses import dataclass

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
from core.analysis_core.statics.deflection import DeflectionCalculator
from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.hp_model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.hp_model.hp_slab import HPSlab


# ------------------------------------------------------------------------------
# Config dataclass
# ------------------------------------------------------------------------------

@dataclass
class SlabConfig:
    """
    Holds all fixed parameters for a C1_x test configuration.
    The only thing that varies across test cases is the prestress level.
    """
    name:               str
    hp_geom:            HPGeometry
    concrete:           Concrete
    fyk:                float
    ftk:                float
    Es:                 float
    epsuk:              float
    density:            float
    constitutive_law:   Elastic
    gamma_s:            float
    reinf_name:         str
    reinf_area:         float       # mm²

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
        hp_slab  = HPSlab(hp_shell, infill)
        return SlabConstruction(hp_slab, test_floor)


# ------------------------------------------------------------------------------
# Configurations
# ------------------------------------------------------------------------------

ALL_CONFIGS = [
    SlabConfig(
        name             = "C1_1",
        hp_geom          = HPGeometry(B=1200, L=6750, Hx=40,  Hy=160, t=40,  dy=100, nt=7),
        concrete         = concrete_c50_uls,
        fyk=fyk_Q95,  ftk=ftk_Q95,  Es=Es_Q95,  epsuk=epsuk_Q95,
        density=density_Q95,  constitutive_law=brittle_elastic_law_Q95,
        gamma_s=1.3,  reinf_name="solidian GRID Q95/95-CCE-38",
        reinf_area       = 50,
    ),
    SlabConfig(
        name             = "C1_2 (C50)",
        hp_geom          = HPGeometry(B=1200, L=6750, Hx=75,  Hy=300, t=70,  dy=50,  nt=8),
        concrete         = concrete_c50_uls,
        fyk=fyk_Q95,  ftk=ftk_Q95,  Es=Es_Q95,  epsuk=epsuk_Q95,
        density=density_Q95,  constitutive_law=brittle_elastic_law_Q95,
        gamma_s=1.3,  reinf_name="solidian GRID Q95/95-CCE-38",
        reinf_area       = 50,
    ),
    SlabConfig(
        name             = "C1_2 (C80)",
        hp_geom          = HPGeometry(B=1200, L=6750, Hx=75,  Hy=300, t=70,  dy=50,  nt=8),
        concrete         = concrete_c80_uls,
        fyk=fyk_Q95,  ftk=ftk_Q95,  Es=Es_Q95,  epsuk=epsuk_Q95,
        density=density_Q95,  constitutive_law=brittle_elastic_law_Q95,
        gamma_s=1.3,  reinf_name="solidian GRID Q95/95-CCE-38",
        reinf_area       = 50,
    ),
    SlabConfig(
        name             = "C1_3",
        hp_geom          = HPGeometry(B=1500, L=6750, Hx=125, Hy=500, t=50,  dy=50,  nt=1),
        concrete         = concrete_c50_uls,
        fyk=fyk_Q142, ftk=ftk_Q142, Es=Es_Q142, epsuk=epsuk_Q142,
        density=density_Q142, constitutive_law=brittle_elastic_law_Q142,
        gamma_s=1.3,  reinf_name="solidian GRID Q142/142-CCE-25",
        reinf_area       = 300,
    ),
    SlabConfig(
        name             = "C1_4",
        hp_geom          = HPGeometry(B=1200, L=6750, Hx=100, Hy=400, t=100, dy=80,  nt=10),
        concrete         = concrete_c55_uls,
        fyk=fyk_Q142, ftk=ftk_Q142, Es=Es_Q142, epsuk=epsuk_Q142,
        density=density_Q142, constitutive_law=brittle_elastic_law_Q142,
        gamma_s=1.3,  reinf_name="solidian GRID Q142/142-CCE-25",
        reinf_area       = 80,
    ),
]

PRESTRESS_LEVELS_PCT = [0, 10, 20, 30, 40, 50]

# ------------------------------------------------------------------------------
# Settings
# ------------------------------------------------------------------------------

COMMON_KWARGS = dict(
    loads=test_loads,
    system=SystemType.SIMPLE_BEAM,
    combination="QUASI_PERMANENT",
    n_intervals=40,
    N_axial_N=0.0,
    constitutive_law="TENSTIFF_PARABOLIC",
    load_history_method="NONE",
    debug=False,
)

# ------------------------------------------------------------------------------
# Run and print
# ------------------------------------------------------------------------------

col = 15
header = (
    f"{'Prestress [%]':>{col}} "
    f"{'Simplified [mm]':>{col}} "
    f"{'Full [mm]':>{col}} "
    f"{'Diff [mm]':>{col}} "
    f"{'Diff [%]':>{col}}"
)
sep = "-" * len(header)

for config in ALL_CONFIGS:

    results = []

    for pct in PRESTRESS_LEVELS_PCT:
        slab = config.build_slab_construction(pct / 100)

        defl_simplified = DeflectionCalculator.calculate_deflection_mm_EC(
            slab_construction=slab,
            m_k_simplification=True,
            **COMMON_KWARGS,
        )
        defl_full = DeflectionCalculator.calculate_deflection_mm_EC(
            slab_construction=slab,
            m_k_simplification=False,
            **COMMON_KWARGS,
        )

        diff_abs = defl_full - defl_simplified
        diff_pct = (diff_abs / defl_full * 100) if defl_full != 0.0 else float("nan")

        results.append({
            "pct":        pct,
            "simplified": defl_simplified,
            "full":       defl_full,
            "diff_abs":   diff_abs,
            "diff_pct":   diff_pct,
        })

    # --- Print table for this config ---
    print(f"\n{config.name} — Deflection (QP): simplification vs full MK")
    print(sep)
    print(header)
    print(sep)

    for r in results:
        print(
            f"{r['pct']:>{col}} "
            f"{r['simplified']:>{col}.3f} "
            f"{r['full']:>{col}.3f} "
            f"{r['diff_abs']:>{col}.3f} "
            f"{r['diff_pct']:>{col}.2f}"
        )

    print(sep)

    max_diff = max(results, key=lambda r: abs(r["diff_abs"]))
    min_diff = min(results, key=lambda r: abs(r["diff_abs"]))

    print(f"Largest  diff : {max_diff['pct']:>2}% prestress → {max_diff['diff_abs']:+.3f} mm  ({max_diff['diff_pct']:+.2f}%)")
    print(f"Smallest diff : {min_diff['pct']:>2}% prestress → {min_diff['diff_abs']:+.3f} mm  ({min_diff['diff_pct']:+.2f}%)")