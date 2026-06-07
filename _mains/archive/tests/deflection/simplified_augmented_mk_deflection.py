import time
from contextlib import contextmanager

from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_slab_construction import (
    test_slab_construction_c1_1,
    test_slab_construction_c1_2_c50,
    test_slab_construction_c1_2_c80,
    test_slab_construction_c1_3,
    test_slab_construction_c1_4,
)
from core.analysis_core.statics.constants import SystemType
from core.analysis_core.statics.deflection import DeflectionCalculator

"""
Author: Elliot Melcer
This file is used to track the runtime of the deflection calculation for different values of
input parameter 'simplification'

Output (24.05.26):

Simplified = True
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                     7.6          7.4          8.4            7.8
c1_2_c50                 9.0          8.6          8.9            8.9
c1_2_c80                 8.8          9.0          9.1            9.0
c1_3                     6.2          6.7          6.5            6.5
c1_4                     8.7          8.1          9.2            8.7

Simplified = 1
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                     9.5          9.8          8.9            9.4
c1_2_c50                 9.5         10.0          9.3            9.6
c1_2_c80                 9.8          9.5          9.1            9.4
c1_3                     6.6          7.5          6.6            6.9
c1_4                     9.9         11.0          9.9           10.3

Simplified = 2
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                    10.0          9.0          9.2            9.4
c1_2_c50                10.2         10.2         10.4           10.3
c1_2_c80                10.6         11.4         10.5           10.8
c1_3                     7.3          7.0          7.0            7.1
c1_4                    10.6         10.8         10.8           10.7

Simplified = 3
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                    11.5         12.1         11.5           11.7
c1_2_c50                12.2         13.1         13.0           12.8
c1_2_c80                12.4         12.7         13.7           12.9
c1_3                     8.7          8.4          8.0            8.4
c1_4                    12.9         14.0         13.4           13.4

Simplified = 4
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                    12.7         11.4         12.0           12.0
c1_2_c50                13.9         12.5         12.9           13.1
c1_2_c80                14.2         16.2         15.2           15.2
c1_3                     9.8         10.0          9.8            9.9
c1_4                    15.9         15.6         14.7           15.4

Simplified = 5
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                    12.5         12.8         12.9           12.7
c1_2_c50                14.2         13.9         15.4           14.5
c1_2_c80                17.3         17.3         15.8           16.8
c1_3                    10.3         10.4         11.2           10.6
c1_4                    14.7         16.0         15.6           15.4

Simplified = False
Slab name          Run 1 [s]    Run 2 [s]    Run 3 [s]    Average [s]
----------------------------------------------------------------------
c1_1                    64.6         63.3         61.4           63.1
c1_2_c50                67.5         68.2         70.0           68.6
c1_2_c80                76.0         76.8         85.0           79.3
c1_3                    56.6         53.6         51.9           54.0
c1_4                    69.4         69.6         71.0           70.0


"""
@contextmanager
def timed(label: str, enabled: bool = True):
    if not enabled:
        yield
        return
    _start = time.perf_counter()
    yield
    print(f"Analysis Time {label}: {time.perf_counter() - _start:.6f} s")

test_slabs = {
    "c1_1": test_slab_construction_c1_1,
    "c1_2_c50": test_slab_construction_c1_2_c50,
    "c1_2_c80": test_slab_construction_c1_2_c80,
    "c1_3": test_slab_construction_c1_3,
    "c1_4": test_slab_construction_c1_4,
}

from structuralcodes.materials.constitutive_laws import Elastic
from structuralcodes.materials.reinforcement import create_reinforcement

from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.hp_model.hp_slab import HPSlab


timed_run = True

import time

simplified = [
    # True,
    1, 2, 3, 4, 5,
    False,
    0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
    0.15
]
n_runs = 1

for simplification in simplified:
    print(f"\nSimplified = {simplification}")
    print(f"{'Slab name':<15} {'Run 1 [s]':>12} {'Run 2 [s]':>12} {'Run 3 [s]':>12} {'Average [s]':>14} {'Deflection [mm]':>17}")
    print("-" * 87)

    for name, slab_construction in test_slabs.items():
        run_times = []
        deflection_qp_simple_mm = 0.0
        for _ in range(n_runs):
            start = time.perf_counter()

            deflection_qp_simple_mm = DeflectionCalculator.calculate_deflection_mm_EC(
                slab_construction=slab_construction,
                loads=test_loads,
                system=SystemType.SIMPLE_BEAM,
                combination="QUASI_PERMANENT",
                n_intervals=40,
                N_axial_N=0.0,
                constitutive_law="TENSTIFF_PARABOLIC",
                load_history_method="NONE",
                m_k_simplification=simplification,
                debug=False,
            )

            elapsed = time.perf_counter() - start
            run_times.append(elapsed)

        average_time = sum(run_times) / len(run_times)

        print(
            f"{name:<15} "
            f"{run_times[0]:>12.1f} "
            f"{run_times[1]:>12.1f} "
            f"{run_times[2]:>12.1f} "
            f"{average_time:>14.1f}"
            f"{deflection_qp_simple_mm:>17.3f}"
        )