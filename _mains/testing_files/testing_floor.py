from _mains.testing_files.testing_materials import infill, sound_insulation, screed
from slab_construction.floor import FloorLayer, Floor

infill_layer = FloorLayer(infill, 0.0)
sound_insulation_layer = FloorLayer(sound_insulation, 12.0)
screed_layer = FloorLayer(screed, 45.0)

reference_infill_layer              = FloorLayer(infill, 30.)
reference_sound_insulation_layer    = FloorLayer(sound_insulation, 20.)
reference_screed_layer              = FloorLayer(screed, 50.)

test_floor = Floor([infill_layer, sound_insulation_layer, screed_layer])
ref_floor = Floor([reference_infill_layer, reference_sound_insulation_layer, reference_screed_layer])