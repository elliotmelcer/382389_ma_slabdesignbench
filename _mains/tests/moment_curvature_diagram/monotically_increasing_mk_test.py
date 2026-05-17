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
from core.analysis_core.section_methods import get_concrete, sls_section, calculate_moment_curvature_sls
from core.analysis_core.statics.new_deflection import DeflectionCalculator
from core.visualization_core.visualization import plot_constitutive_law_concrete, plot_moment_curvature

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
    # "c1_2_c50": test_slab_construction_c1_2_c50,
    # "c1_2_c80": test_slab_construction_c1_2_c80,
    "c1_3": test_slab_construction_c1_3,
    # "c1_4": test_slab_construction_c1_4,
}

constitutive_law = [
    # "NONE_PARABOLIC",
    "FCTM_PARABOLIC",
    # "TENSTIFF_PARABOLIC",
    # "ELASTIC_ELASTIC"
]

timed_run = False
x = 0.5

for name, slab_construction in test_slabs.items():
    for c_law in constitutive_law:
        with timed("Deflection  ", timed_run):
            section = slab_construction.slab.section_at(x)

            moment_curvature = calculate_moment_curvature_sls(
                section             = section,
                n                   = 0.0,
                constitutive_law    = c_law,
                simplification= False,
            )

        plot_moment_curvature(moment_curvature)

plt.show()