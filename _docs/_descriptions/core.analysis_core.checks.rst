The ``checks`` subpackage implements the structural, constructional, and acoustic
verifications that form the constraints of the HP-shell optimization problem.
Each check category is defined through an abstract base class prescribing a
``calculate_utilization()`` method, ensuring a uniform interface across all
verification types: ``StructuralCheck`` (ULS/SLS bending), ``ConstructionCheck``
(geometric and detailing rules), ``AcousticCheck`` (sound insulation and impact
noise), and ``ModelingCheck`` (numerical plausibility). Checks are organized
across four modules corresponding to verification categories A--D and Z from
the original Grasshopper implementation by Loutfi :cite:`loutfi_2023`.
