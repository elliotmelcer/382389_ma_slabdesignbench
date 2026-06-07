from structuralcodes.materials.reinforcement import Reinforcement
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes import set_design_code

set_design_code('ec2_2004')

r = create_reinforcement(fyk = 2200 ,ftk=2200, Es=220000, epsuk=10*1**(-3), density=1800)



