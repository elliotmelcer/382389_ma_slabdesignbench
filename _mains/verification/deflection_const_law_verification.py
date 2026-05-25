import time
from contextlib import contextmanager

from matplotlib import pyplot as plt
from tabulate import tabulate

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import (
    test_slab_construction_c1_1,
    test_slab_construction_c1_2_c50,
    test_slab_construction_c1_2_c80,
    test_slab_construction_c1_3,
    test_slab_construction_c1_4,
)
from core.analysis_core.section_methods import get_concrete, sls_section_EC
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator


"""
This file is used to show the difference in deflection when using different calculation methods and 
constitutive laws for concrete. This was tested on designs C.1_1, C.1_2.1, C.1_2.2, C.1_3 and C.1_4.

Results (23.05.26)

============================================================
DEFLECTION RESULTS — QUASI-PERMANENT COMBINATION
============================================================

  c1_1
╭───────────────────────┬────────────────────┬───────────────────╮
│ load_history_method   │ constitutive_law   │   Deflection [mm] │
├───────────────────────┼────────────────────┼───────────────────┤
│ NONE                  │ NONE_PARABOLIC     │               7.2 │
│ NONE                  │ FCTM_PARABOLIC     │              7.18 │
│ NONE                  │ TENSTIFF_PARABOLIC │              7.18 │
│ NONE                  │ ELASTIC_ELASTIC    │              7.26 │
│ FACTOR_EC             │ -                  │              7.24 │
╰───────────────────────┴────────────────────┴───────────────────╯

  c1_2_c50
╭───────────────────────┬────────────────────┬───────────────────╮
│ load_history_method   │ constitutive_law   │   Deflection [mm] │
├───────────────────────┼────────────────────┼───────────────────┤
│ NONE                  │ NONE_PARABOLIC     │             -8.63 │
│ NONE                  │ FCTM_PARABOLIC     │             -8.62 │
│ NONE                  │ TENSTIFF_PARABOLIC │             -8.62 │
│ NONE                  │ ELASTIC_ELASTIC    │             -8.58 │
│ FACTOR_EC             │ -                  │             -8.58 │
╰───────────────────────┴────────────────────┴───────────────────╯

  c1_2_c80
╭───────────────────────┬────────────────────┬───────────────────╮
│ load_history_method   │ constitutive_law   │   Deflection [mm] │
├───────────────────────┼────────────────────┼───────────────────┤
│ NONE                  │ NONE_PARABOLIC     │             -7.26 │
│ NONE                  │ FCTM_PARABOLIC     │             -7.26 │
│ NONE                  │ TENSTIFF_PARABOLIC │             -7.26 │
│ NONE                  │ ELASTIC_ELASTIC    │             -7.23 │
│ FACTOR_EC             │ -                  │             -7.23 │
╰───────────────────────┴────────────────────┴───────────────────╯

  c1_3
╭───────────────────────┬────────────────────┬───────────────────╮
│ load_history_method   │ constitutive_law   │   Deflection [mm] │
├───────────────────────┼────────────────────┼───────────────────┤
│ NONE                  │ NONE_PARABOLIC     │             13.74 │
│ NONE                  │ FCTM_PARABOLIC     │             10.83 │
│ NONE                  │ TENSTIFF_PARABOLIC │               3.6 │
│ NONE                  │ ELASTIC_ELASTIC    │              3.13 │
│ FACTOR_EC             │ -                  │             10.49 │
╰───────────────────────┴────────────────────┴───────────────────╯

  c1_4
╭───────────────────────┬────────────────────┬───────────────────╮
│ load_history_method   │ constitutive_law   │   Deflection [mm] │
├───────────────────────┼────────────────────┼───────────────────┤
│ NONE                  │ NONE_PARABOLIC     │             -8.97 │
│ NONE                  │ FCTM_PARABOLIC     │             -8.97 │
│ NONE                  │ TENSTIFF_PARABOLIC │             -8.97 │
│ NONE                  │ ELASTIC_ELASTIC    │             -8.92 │
│ FACTOR_EC             │ -                  │             -8.92 │
╰───────────────────────┴────────────────────┴───────────────────╯

============================================================

"""

@contextmanager
def timed(label: str, enabled: bool = True):
    if not enabled:
        yield
        return
    start = time.perf_counter()
    yield
    print(f"Analysis Time {label}: {time.perf_counter() - start:.6f} s")


test_slabs = {
    "c1_1":     test_slab_construction_c1_1,
    "c1_2_c50": test_slab_construction_c1_2_c50,
    "c1_2_c80": test_slab_construction_c1_2_c80,
    "c1_3":     test_slab_construction_c1_3,
    "c1_4":     test_slab_construction_c1_4,
}

constitutive_law = [
    "NONE_PARABOLIC",
    "FCTM_PARABOLIC",
    "TENSTIFF_PARABOLIC",
    "ELASTIC_ELASTIC",
]

timed_run = True
results = []  # collect all rows

for name, slab_construction in test_slabs.items():
    for c_law in constitutive_law:
        deflection_qp_mm = DeflectionCalculator.calculate_deflection_mm_EC(
            slab_construction   = slab_construction,
            loads               = test_loads,
            system              = SystemType.SIMPLE_BEAM,
            combination         = "QUASI_PERMANENT",
            n_intervals         = 40,
            N_axial_N           = 0.0,
            constitutive_law    = c_law,
            load_history_method = "NONE",
            m_k_simplification  = False,
            debug               = False,
            extended_debug      = False,
        )

        results.append({
            "Slab":                name,
            "load_history_method": "NONE",
            "constitutive_law":    c_law,
            "Deflection [mm]":     f"{deflection_qp_mm:.2f}",
        })

    # Factor method row
    deflection_factor_qp_mm = DeflectionCalculator.calculate_deflection_mm_EC(
        slab_construction   = slab_construction,
        loads               = test_loads,
        system              = SystemType.SIMPLE_BEAM,
        combination         = "QUASI_PERMANENT",
        n_intervals         = 40,
        N_axial_N           = 0.0,
        constitutive_law    = "NONE_PARABOLIC",
        load_history_method = "FACTOR_EC",
        m_k_simplification  = False,
        debug               = False,
        extended_debug      = False,
    )

    results.append({
        "Slab":                name,
        "load_history_method": "FACTOR_EC",
        "constitutive_law":    "-",
        "Deflection [mm]":     f"{deflection_factor_qp_mm:.2f}",
    })

# --- Tabellarische Ausgabe ---
print("\n" + "=" * 60)
print("DEFLECTION RESULTS — QUASI-PERMANENT COMBINATION")
print("=" * 60)

# Ergebnisse nach Slab gruppieren

grouped = {}
for row in results:
    grouped.setdefault(row["Slab"], []).append(row)

for slab_name, rows in grouped.items():
    print(f"\n  {slab_name}")

    table = [
        [
            r["load_history_method"],
            r["constitutive_law"],
            r["Deflection [mm]"],
        ]
        for r in rows
    ]

    print(tabulate(
        table,
        headers=[
            "load_history_method",
            "constitutive_law",
            "Deflection [mm]",
        ],
        tablefmt="rounded_outline",
        colalign=("left", "left", "right"),
    ))

print("\n" + "=" * 60 + "\n")

plt.show()