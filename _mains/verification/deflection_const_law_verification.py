import time
from contextlib import contextmanager

from matplotlib import pyplot as plt

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
Output (27.03.26):
 - see simplified vs. Full MK-Line Verformung Vergleich.xslx

Conclusions:
 - the more points, the longer it takes

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
    # "c1_1": test_slab_construction_c1_1,
    "c1_2_c50": test_slab_construction_c1_2_c50,
    "c1_2_c80": test_slab_construction_c1_2_c80,
    "c1_3": test_slab_construction_c1_3,
    "c1_4": test_slab_construction_c1_4,
}

constitutive_law = [
    "NONE_PARABOLIC",
    "FCTM_PARABOLIC",
    "TENSTIFF_PARABOLIC",
    "ELASTIC_ELASTIC"
]

timed_run = True

for name, slab_construction in test_slabs.items():
    for c_law in constitutive_law:
        with timed("Deflection  ", timed_run):
            deflection_qp_mm = DeflectionCalculator.calculate_deflection_mm_EC(
                slab_construction   = slab_construction,
                loads               = test_loads,
                system              = SystemType.SIMPLE_BEAM,
                combination         = "QUASI-PERMANENT",
                n_intervals         = 40,
                N_axial_N           = 0.0,
                constitutive_law    = c_law,
                load_history_method = "FACTOR_EC",
                m_k_simplification  = False,
                debug               = True,
                extended_debug      = False,
            )


        sls_sec = sls_section_EC(slab_construction.slab.section_at(0.5), c_law)
        sls_conc = get_concrete(sls_sec)

        print(f"{name}:")
        print(f"  Deflection ({c_law}): {deflection_qp_mm:.3f} mm")
        print()

plt.show()