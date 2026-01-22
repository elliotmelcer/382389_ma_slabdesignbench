from _mains.testing_files.testing_materials import infill, sound_insulation, screed
from slab_construction.slab_construction import FloorLayer, Floor

infill_layer = FloorLayer(infill, 0.0)
sound_insulation_layer = FloorLayer(sound_insulation, 12.0)
screed_layer = FloorLayer(screed, 45.0)

test_floor = Floor([infill_layer, sound_insulation_layer, screed_layer])