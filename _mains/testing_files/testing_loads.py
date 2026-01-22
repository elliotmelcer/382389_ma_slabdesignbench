from core.analysis_core.loads import Loads

live_loads = [3.0] #kN/m²

psi_0_values = [1.0]
psi_1_values = [1.0]
psi_2_values = [0.3]

test_loads = Loads(live_loads, psi_0_values, psi_1_values, psi_2_values)