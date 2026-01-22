from structuralcodes.materials.reinforcement import create_reinforcement

carb_epsuk = 10*1**(-3)

carbon = create_reinforcement(fyk = 2200 ,ftk=2200, Es=220000, epsuk=carb_epsuk, density=1800, design_code='CFRP')

strain = 0.01

stress = carbon.constitutive_law.get_stress(strain)

print(f"the stress is {stress}")
