"""
Discretization convergence test for HPShell.section_at(n=...).

Tests n ∈ [100, 50, 30, 20, 10] for:
  - Mcr   (cracking moment,        SLS, midspan)
  - Mu    (ultimate bending moment, ULS, midspan)
  - w_max (deflection,             SLS, quasi-permanent, simple beam)

n=100 ist der Produktiv-Default (hardcoded in HPShell.section_at). Alle
kleineren n werden relativ zur n=100 Baseline ausgewertet. Außerdem wird
die Laufzeit jeder Auswertung gemessen, damit man Genauigkeit vs. Speed
direkt vergleichen kann.

Für die Deflection muss `HPShell.section_at` temporär gepatcht werden, weil
DeflectionCalculator intern `slab.section_at(x)` aufruft und das n nicht
durchreichen kann.
"""
import time
from contextlib import contextmanager

import numpy as np
from matplotlib import pyplot as plt

from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.sections import GenericSection

from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from _mains.testing_files.testing_loads import test_loads
from core.analysis_core.section_methods import (
    calculate_cracking_moment_sls_Nmm_EC,
    calculate_bending_strength_uls_Nmm_EC,
)
from core.analysis_core.statics.deflection import DeflectionCalculator
from core.analysis_core.statics.constants import SystemType
from core.unit_core import Nmm_to_kNm
from slab_construction.slabs.hp_slab.hp_model.hp_shell import HPShell


set_design_code('ec2_2004')


# ----------------------------------------------------------------------------
# Settings — hier ggf. das Test-Slab oder x_norm tauschen
# ----------------------------------------------------------------------------
N_VALUES = [100, 50, 30, 20, 10]   # Baseline ist N_VALUES[0]
X_NORM   = 0.5                     # Midspan für Mcr / Mu Punktauswertung

slab_construction = test_slab_construction_c1_4
hp_shell          = slab_construction.slab.hp_shell


# ----------------------------------------------------------------------------
# Build section mit variablem n (spiegelt HPShell.section_at)
# ----------------------------------------------------------------------------
def build_section_with_n(
        shell: HPShell,
        x_norm: float,
        n: int,
        name: str = None,
) -> GenericSection:
    """Mirrors HPShell.section_at() but lets the caller choose n."""
    if not 0.0 <= x_norm <= 1.0:
        raise ValueError(f"x_norm must be in [0, 1], got {x_norm}")

    x_internal = x_norm - 0.5

    geom = SurfaceGeometry(
        poly=shell.hp_geometry.polygon_section_at(x=x_internal, n=n),
        material=shell.concrete,
    )

    d = float(np.sqrt(4 * shell.reinf_area / np.pi))
    for pt in shell.hp_geometry.tendon_coords_at_x(x=x_internal):
        geom = add_reinforcement(geom, pt, d, shell.reinforcement)

    return GenericSection(geom, name=name or shell.name)


@contextmanager
def override_shell_n(shell: HPShell, n: int):
    """
    Ersetzt shell.section_at vorübergehend durch eine Variante mit gewähltem n.
    HPSlab.section_at delegiert direkt an hp_shell.section_at, daher reicht es
    den Shell zu patchen.
    """
    original = shell.section_at

    def patched(x, name=None, _shell=shell, _n=n):
        return build_section_with_n(_shell, x, _n, name=name)

    shell.section_at = patched
    try:
        yield
    finally:
        shell.section_at = original


# ----------------------------------------------------------------------------
# Timing helper
# ----------------------------------------------------------------------------
def timed(func, *args, **kwargs):
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    dt = time.perf_counter() - t0
    return result, dt


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
print("=" * 95)
print("Discretization convergence test")
print(f"  Slab construction : test_slab_construction_c1_4")
print(f"  Section position  : x/L = {X_NORM}")
print(f"  Deflection load   : SimpleBeam, QUASI_PERMANENT, test_loads")
print("=" * 95)

results = []

for n in N_VALUES:
    print(f"\n--- n = {n:>3}  (polygon vertices: {2 * n}) ---")

    # --- Mcr -----------------------------------------------------------------
    section = build_section_with_n(hp_shell, X_NORM, n)
    mcr_res, t_mcr = timed(calculate_cracking_moment_sls_Nmm_EC, section, n=0)
    if mcr_res.get("valid", True) and mcr_res.get("m_cr") is not None and np.isfinite(mcr_res["m_cr"]):
        mcr_kNm = -Nmm_to_kNm(mcr_res["m_cr"])
    else:
        mcr_kNm = float("nan")
        print(f"  Mcr invalid: {mcr_res.get('reason', '<no reason>')}")
    print(f"  Mcr        = {mcr_kNm:>10.4f} kNm   ({t_mcr * 1000:>7.1f} ms)")

    # --- Mu ------------------------------------------------------------------
    section = build_section_with_n(hp_shell, X_NORM, n)
    mu_res, t_mu = timed(calculate_bending_strength_uls_Nmm_EC, section, n=0)
    if mu_res.get("valid", True) and mu_res.get("m_u") is not None:
        mu_kNm = -Nmm_to_kNm(mu_res["m_u"])
    else:
        mu_kNm = float("nan")
        print(f"  Mu invalid: {mu_res.get('reason', '<no reason>')}")
    print(f"  Mu         = {mu_kNm:>10.4f} kNm   ({t_mu * 1000:>7.1f} ms)")

    # --- Deflection ----------------------------------------------------------
    with override_shell_n(hp_shell, n):
        try:
            w_max, t_w = timed(
                DeflectionCalculator.calculate_deflection_mm_EC,
                slab_construction,
                test_loads,
                system=SystemType.SIMPLE_BEAM,
                combination="QUASI_PERMANENT",
            )
        except Exception as e:
            w_max, t_w = float("nan"), float("nan")
            print(f"  Deflection failed: {e}")

    print(f"  Deflection = {w_max:>10.4f} mm    ({t_w * 1000:>7.1f} ms)")

    results.append({
        "n":         n,
        "mcr_kNm":   mcr_kNm,
        "mu_kNm":    mu_kNm,
        "w_max_mm":  w_max,
        "t_mcr_ms":  t_mcr * 1000,
        "t_mu_ms":   t_mu  * 1000,
        "t_defl_ms": t_w   * 1000,
    })


# ----------------------------------------------------------------------------
# Summary table — relative to n = N_VALUES[0]
# ----------------------------------------------------------------------------
baseline = results[0]


def rel_err(val, ref):
    if not np.isfinite(val) or not np.isfinite(ref) or ref == 0:
        return float("nan")
    return (val - ref) / ref * 100.0


print()
print("=" * 95)
print(f"Summary (baseline: n = {baseline['n']})")
print("=" * 95)
print(f"{'n':>4} | "
      f"{'Mcr [kNm]':>10} {'ΔMcr [%]':>9} | "
      f"{'Mu [kNm]':>10} {'ΔMu [%]':>8} | "
      f"{'w [mm]':>8} {'Δw [%]':>7} | "
      f"{'t_Mcr ms':>9} {'t_Mu ms':>9} {'t_w ms':>9}")
print("-" * 95)
for r in results:
    print(f"{r['n']:>4} | "
          f"{r['mcr_kNm']:>10.4f} {rel_err(r['mcr_kNm'], baseline['mcr_kNm']):>+9.3f} | "
          f"{r['mu_kNm']:>10.4f} {rel_err(r['mu_kNm'], baseline['mu_kNm']):>+8.3f} | "
          f"{r['w_max_mm']:>8.4f} {rel_err(r['w_max_mm'], baseline['w_max_mm']):>+7.3f} | "
          f"{r['t_mcr_ms']:>9.1f} {r['t_mu_ms']:>9.1f} {r['t_defl_ms']:>9.1f}")
print("=" * 95)


# ----------------------------------------------------------------------------
# Plot
# ----------------------------------------------------------------------------
ns       = [r["n"]                                              for r in results]
mcr_err  = [rel_err(r["mcr_kNm"],  baseline["mcr_kNm"])         for r in results]
mu_err   = [rel_err(r["mu_kNm"],   baseline["mu_kNm"])          for r in results]
w_err    = [rel_err(r["w_max_mm"], baseline["w_max_mm"])        for r in results]
total_ms = [r["t_mcr_ms"] + r["t_mu_ms"] + r["t_defl_ms"]       for r in results]

fig, (ax_err, ax_time) = plt.subplots(1, 2, figsize=(12, 4.5))

ax_err.plot(ns, mcr_err, "o-", label="Mcr")
ax_err.plot(ns, mu_err,  "s-", label="Mu")
ax_err.plot(ns, w_err,   "d-", label="w_max")
ax_err.axhline(0, color="black", linewidth=0.8)
ax_err.set_xlabel("n (points per polygon edge)")
ax_err.set_ylabel(f"Relative error vs n = {baseline['n']} [%]")
ax_err.set_title("Discretization error")
ax_err.invert_xaxis()
ax_err.grid(True, alpha=0.3)
ax_err.legend()

ax_time.plot(ns, total_ms, "o-", color="black")
ax_time.set_xlabel("n (points per polygon edge)")
ax_time.set_ylabel("Total time per evaluation [ms]")
ax_time.set_title("Cost (Mcr + Mu + Deflection)")
ax_time.invert_xaxis()
ax_time.grid(True, alpha=0.3)

fig.tight_layout()
plt.show()