The ``statics`` subpackage provides fundamental structural mechanics methods
used throughout ``analysis_core``. It covers load combinations for ULS and SLS
according to Eurocode 1 (``loads.py``), bending moment calculation for continuous
beams and cantilevers via tabulated coefficients (``internal_forces.py``), and
deflection calculation for the serviceability limit state (``deflection.py``).
Currently fully implemented for single-span beams under uniform distributed loads;
frameworks for multi-span systems and cantilevers are in place for future extension.
