from core.analysis_core.section_methods import get_concrete
from _mains.tests.hp_shell_geometry_test import hp_section_sls
from _mains.testing_files.testing_materials import concrete_c50_sls

epsmin_section, _ = get_concrete(hp_section_sls).constitutive_law.get_ultimate_strain()

print("eps_cu1 from section = ", get_concrete(hp_section_sls).constitutive_law._eps_cu1)
eps_cu1 = concrete_c50_sls.constitutive_law._eps_cu1
print("eps_cu1 from material = ", concrete_c50_sls.constitutive_law._eps_cu1)
print("eps_c1 from material = ", concrete_c50_sls.constitutive_law._eps_c1)
print("k from material = ", concrete_c50_sls.k_sargin)
print("Ecm from material = ", concrete_c50_sls.Ecm)
print("concrete law = ", concrete_c50_sls.constitutive_law._name)
print("sigma_cu1 from material = ", concrete_c50_sls.constitutive_law.get_stress(eps_cu1))