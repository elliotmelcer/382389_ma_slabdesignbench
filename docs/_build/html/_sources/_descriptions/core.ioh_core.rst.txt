``ioh_core`` is the interface between the optimization problems defined in
``slab_construction`` and the IOHexperimenter benchmarking framework. It handles
problem construction from CSV definitions, caches repeated function evaluations
for efficiency, and exposes a single entry point ``run_experiment()`` for
executing complete benchmarking studies.
