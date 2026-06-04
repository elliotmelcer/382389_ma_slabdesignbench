"""
Discretization convergence test for HPShell.section_at(n=...).

Tests n ∈ [100, 50, 30, 20, 10] for:
  - Mcr   (cracking moment,        SLS, midspan)
  - Mu    (ultimate bending moment, ULS, midspan)
  - w_max (deflection,             SLS, quasi-permanent, simple beam)

n=100 ist der Produktiv-Default (hardcoded in HPShell.section_at). Alle
kleineren n werden relativ zur n=100 Baseline ausgewertet.

Genauigkeit (Mcr/Mu/w_max) ist deterministisch → 1 Messung reicht.
Laufzeiten haben OS-Jitter → wir messen N_REPEATS-mal und nehmen den Median
mit min/max als Streuband. Davor noch ein Warmup-Run (verworfen), um Imports,
Caches und JIT zu erwärmen.

Hinweis: Mit N_REPEATS = 3 und ~60 s pro Evaluation läuft das Skript ca.
5 × 3 × 60 s ≈ 15 Minuten. Bei Bedarf N_REPEATS oder N_VALUES anpassen.
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
# Settings — hier ggf. Test-Slab, x_norm oder N_REPEATS tauschen
# ----------------------------------------------------------------------------
N_VALUES   = [100, 50, 30, 20, 10]   # Baseline ist N_VALUES[0]
X_NORM     = 0.5                     # Midspan für Mcr / Mu Punktauswertung
N_REPEATS  = 3                       # Wiederholungen pro n für Timing
WARMUP_N   = 50                      # n für den verworfenen Warmup-Run

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
    """Patch shell.section_at temporarily so DeflectionCalculator sees custom n."""
    original = shell.section_at

    def patched(x, name=None, _shell=shell, _n=n):
        return build_section_with_n(_shell, x, _n, name=name)

    shell.section_at = patched
    try:
        yield
    finally:
        shell.section_at = original


# ----------------------------------------------------------------------------
# Timing helpers
# ----------------------------------------------------------------------------
def timed_repeated(label, func, *args, n_repeats=N_REPEATS, **kwargs):
    """
    Run func n_repeats times, return (last_result, [times_in_seconds]).
    Result of every run is identical (deterministic) — last one is kept for the
    value/quality reporting.
    """
    times = []
    result = None
    for i in range(n_repeats):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        dt = time.perf_counter() - t0
        times.append(dt)
        print(f"    {label} run {i + 1}/{n_repeats}: {dt * 1000:>8.1f} ms")
    return result, times


def summarize_times(times):
    """Return (median_ms, min_ms, max_ms)."""
    arr_ms = np.array(times) * 1000.0
    return float(np.median(arr_ms)), float(np.min(arr_ms)), float(np.max(arr_ms))


# ----------------------------------------------------------------------------
# Warmup — verworfen, nur damit Imports/Caches/JIT warm sind
# ----------------------------------------------------------------------------
print("=" * 95)
print(f"Warmup (n = {WARMUP_N}, discarded)")
print("=" * 95)
_warm_section = build_section_with_n(hp_shell, X_NORM, WARMUP_N)
_ = calculate_cracking_moment_sls_Nmm_EC(_warm_section, n=0)
_ = calculate_bending_strength_uls_Nmm_EC(_warm_section, n=0)
with override_shell_n(hp_shell, WARMUP_N):
    _ = DeflectionCalculator.calculate_deflection_mm_EC(
        slab_construction,
        test_loads,
        system=SystemType.SIMPLE_BEAM,
        combination="QUASI_PERMANENT",
    )
print("  done.\n")


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
print("=" * 95)
print("Discretization convergence test")
print(f"  Slab construction : test_slab_construction_c1_4")
print(f"  Section position  : x/L = {X_NORM}")
print(f"  Deflection load   : SimpleBeam, QUASI_PERMANENT, test_loads")
print(f"  Repeats per timing: {N_REPEATS}")
print("=" * 95)

results = []

for n in N_VALUES:
    print(f"\n--- n = {n:>3}  (polygon vertices: {2 * n}) ---")

    # --- Mcr -----------------------------------------------------------------
    print("  Mcr:")
    section = build_section_with_n(hp_shell, X_NORM, n)
    mcr_res, mcr_times = timed_repeated(
        "Mcr", calculate_cracking_moment_sls_Nmm_EC, section, n=0,
    )
    if mcr_res.get("valid", True) and mcr_res.get("m_cr") is not None and np.isfinite(mcr_res["m_cr"]):
        mcr_kNm = -Nmm_to_kNm(mcr_res["m_cr"])
    else:
        mcr_kNm = float("nan")
        print(f"    Mcr invalid: {mcr_res.get('reason', '<no reason>')}")

    # --- Mu ------------------------------------------------------------------
    print("  Mu:")
    section = build_section_with_n(hp_shell, X_NORM, n)
    mu_res, mu_times = timed_repeated(
        "Mu", calculate_bending_strength_uls_Nmm_EC, section, n=0,
    )
    if mu_res.get("valid", True) and mu_res.get("m_u") is not None:
        mu_kNm = -Nmm_to_kNm(mu_res["m_u"])
    else:
        mu_kNm = float("nan")
        print(f"    Mu invalid: {mu_res.get('reason', '<no reason>')}")

    # --- Deflection ----------------------------------------------------------
    print("  Deflection:")
    with override_shell_n(hp_shell, n):
        try:
            w_max, w_times = timed_repeated(
                "w_max",
                DeflectionCalculator.calculate_deflection_mm_EC,
                slab_construction,
                test_loads,
                system=SystemType.SIMPLE_BEAM,
                combination="QUASI_PERMANENT",
            )
        except Exception as e:
            w_max, w_times = float("nan"), [float("nan")] * N_REPEATS
            print(f"    Deflection failed: {e}")

    results.append({
        "n":         n,
        "mcr_kNm":   mcr_kNm,
        "mu_kNm":    mu_kNm,
        "w_max_mm":  w_max,
        "mcr_times": summarize_times(mcr_times),  # (median, min, max) in ms
        "mu_times":  summarize_times(mu_times),
        "w_times":   summarize_times(w_times),
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
print("=" * 110)
print(f"Summary (baseline: n = {baseline['n']}, timings = median over {N_REPEATS} runs)")
print("=" * 110)
print(f"{'n':>4} | "
      f"{'Mcr [kNm]':>10} {'ΔMcr [%]':>9} | "
      f"{'Mu [kNm]':>10} {'ΔMu [%]':>8} | "
      f"{'w [mm]':>8} {'Δw [%]':>7} | "
      f"{'t_Mcr ms':>11} {'t_Mu ms':>11} {'t_w ms':>13}")
print("-" * 110)
for r in results:
    t_mcr_med, t_mcr_min, t_mcr_max = r["mcr_times"]
    t_mu_med,  t_mu_min,  t_mu_max  = r["mu_times"]
    t_w_med,   t_w_min,   t_w_max   = r["w_times"]
    print(f"{r['n']:>4} | "
          f"{r['mcr_kNm']:>10.4f} {rel_err(r['mcr_kNm'], baseline['mcr_kNm']):>+9.3f} | "
          f"{r['mu_kNm']:>10.4f} {rel_err(r['mu_kNm'], baseline['mu_kNm']):>+8.3f} | "
          f"{r['w_max_mm']:>8.4f} {rel_err(r['w_max_mm'], baseline['w_max_mm']):>+7.3f} | "
          f"{t_mcr_med:>7.1f} ±{(t_mcr_max - t_mcr_min) / 2:>3.0f} "
          f"{t_mu_med:>7.1f} ±{(t_mu_max - t_mu_min) / 2:>3.0f} "
          f"{t_w_med:>9.1f} ±{(t_w_max - t_w_min) / 2:>3.0f}")
print("=" * 110)
print("Timing format: median ± (max-min)/2 [ms]")


# ----------------------------------------------------------------------------
# Plot
# ----------------------------------------------------------------------------
ns      = [r["n"]                                       for r in results]
mcr_err = [rel_err(r["mcr_kNm"],  baseline["mcr_kNm"])  for r in results]
mu_err  = [rel_err(r["mu_kNm"],   baseline["mu_kNm"])   for r in results]
w_err   = [rel_err(r["w_max_mm"], baseline["w_max_mm"]) for r in results]

# Totals (Mcr + Mu + Deflection) — sum medians, propagate min/max conservatively
total_med = [r["mcr_times"][0] + r["mu_times"][0] + r["w_times"][0] for r in results]
total_min = [r["mcr_times"][1] + r["mu_times"][1] + r["w_times"][1] for r in results]
total_max = [r["mcr_times"][2] + r["mu_times"][2] + r["w_times"][2] for r in results]

# yerr für errorbar: (median - min, max - median)
yerr_lo = [med - lo for med, lo in zip(total_med, total_min)]
yerr_hi = [hi - med for hi, med in zip(total_max, total_med)]

fig, (ax_err, ax_time) = plt.subplots(1, 2, figsize=(13, 4.8))

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

ax_time.errorbar(
    ns, total_med,
    yerr=[yerr_lo, yerr_hi],
    fmt="o-", color="black", capsize=4,
    label=f"median ± min/max ({N_REPEATS} runs)",
)
ax_time.set_xlabel("n (points per polygon edge)")
ax_time.set_ylabel("Total time per evaluation [ms]")
ax_time.set_title("Cost (Mcr + Mu + Deflection)")
ax_time.invert_xaxis()
ax_time.grid(True, alpha=0.3)
ax_time.legend()

fig.tight_layout()
plt.show()