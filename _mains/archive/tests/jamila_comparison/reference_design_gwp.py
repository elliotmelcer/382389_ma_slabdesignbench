from pathlib import Path

from _mains.testing_files.testing_slab_construction import test_slab_construction_ref
from _mains.testing_files.testing_gwp_cost_data import ConcreteCO2Registry, ReinforcementCO2Registry
from core.unit_core import mm3_to_m3

"""
File for Debugging differences for cost and gwp of reference hp slab between slabdesignbench and loutfis grasshopper code
"""

slab_con = test_slab_construction_ref

# ──────────────────────────────────────────────────────────────────────────────
# SETUP
# ──────────────────────────────────────────────────────────────────────────────

_hp_shell    = slab_con.slab.hp_shell
concrete_uls = _hp_shell.concrete
reinf        = _hp_shell.reinforcement
reinf_id     = reinf.name.split(" prestressed")[0]

# ──────────────────────────────────────────────────────────────────────────────
# VOLUMES & MASS
# ──────────────────────────────────────────────────────────────────────────────

concrete_m3      = mm3_to_m3(_hp_shell.hp_geometry.volume())
reinforcement_m3 = mm3_to_m3(_hp_shell.total_reinforcement_volume())
reinforcement_kg = reinforcement_m3 * reinf.density   # [kg]

# ──────────────────────────────────────────────────────────────────────────────
# GWP INTENSITIES
# ──────────────────────────────────────────────────────────────────────────────

gwp_concrete_kg_m3      = ConcreteCO2Registry.gwp(concrete_uls)       # [kg CO₂-eq / m³]
gwp_reinforcement_kg_kg = ReinforcementCO2Registry.gwp(reinf_id)      # [kg CO₂-eq / kg]

# ──────────────────────────────────────────────────────────────────────────────
# COST INTENSITIES
# ──────────────────────────────────────────────────────────────────────────────

cost_concrete_eur_m3      = ConcreteCO2Registry.cost(concrete_uls)    # [€ / m³]
cost_reinforcement_eur_kg = ReinforcementCO2Registry.cost(reinf_id)   # [€ / kg]

# ──────────────────────────────────────────────────────────────────────────────
# GWP TOTALS  [kg CO₂-eq]
# ──────────────────────────────────────────────────────────────────────────────

gwp_concrete_kg      = gwp_concrete_kg_m3      * concrete_m3
gwp_reinforcement_kg = gwp_reinforcement_kg_kg * reinforcement_kg
gwp_total_kg         = gwp_concrete_kg + gwp_reinforcement_kg

# ──────────────────────────────────────────────────────────────────────────────
# COST TOTALS  [€]
# ──────────────────────────────────────────────────────────────────────────────

cost_concrete_eur      = cost_concrete_eur_m3      * concrete_m3
cost_reinforcement_eur = cost_reinforcement_eur_kg * reinforcement_kg
cost_total_eur         = cost_concrete_eur + cost_reinforcement_eur

# ──────────────────────────────────────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────────────────────────────────────

print("=" * 55)
print("GWP & COST CALCULATION  —  test_slab_construction_ref")
print("=" * 55)

print(f"\n[VOLUMES & MASS]")
print(f"  Concrete:      {concrete_m3:.6f} m³")
print(f"  Reinforcement: {reinforcement_m3:.6f} m³  →  {reinforcement_kg:.3f} kg")

print(f"\n[GWP INTENSITIES]")
print(f"  Concrete:      {gwp_concrete_kg_m3:.1f} kg CO₂-eq / m³")
print(f"  Reinforcement: {gwp_reinforcement_kg_kg:.1f} kg CO₂-eq / kg")

print(f"\n[GWP TOTALS]")
print(f"  Concrete:      {gwp_concrete_kg:.3f} kg CO₂-eq")
print(f"  Reinforcement: {gwp_reinforcement_kg:.3f} kg CO₂-eq")
print(f"  ─────────────────────────────────────────")
print(f"  Total:         {gwp_total_kg:.3f} kg CO₂-eq")

print(f"\n[COST INTENSITIES]")
print(f"  Concrete:      {cost_concrete_eur_m3:.1f} € / m³")
print(f"  Reinforcement: {cost_reinforcement_eur_kg:.1f} € / kg")

print(f"\n[COST TOTALS]")
print(f"  Concrete:      {cost_concrete_eur:.2f} €")
print(f"  Reinforcement: {cost_reinforcement_eur:.2f} €")
print(f"  ─────────────────────────────────────────")
print(f"  Total:         {cost_total_eur:.2f} €")
print("=" * 55)