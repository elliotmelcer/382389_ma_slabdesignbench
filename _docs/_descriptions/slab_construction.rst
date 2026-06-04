``slab_construction`` contains the structural models of the slab systems.
It defines a modular, extensible class hierarchy --- ``Slab``, ``OneWaySlab``,
``TwoWaySlab`` --- that standardizes how different slab types expose their
geometry and cross-sections. The ``hp_slab`` subpackage contains the first
fully implemented slab type, including objective function and constraints for
the HP-shell optimization problem.
