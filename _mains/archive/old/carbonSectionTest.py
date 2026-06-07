"""Quickstart example."""

from shapely import Polygon

from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.materials.concrete import create_concrete
from structuralcodes.materials.reinforcement import create_reinforcement
from structuralcodes.sections import GenericSection
from structuralcodes.materials.reinforcement import create_reinforcement
import matplotlib.pyplot as plt

# Set the active design code
set_design_code('ec2_2004')

# Create a concrete and a reinforcement
fck = 45
fyk = 500
ftk = 550
Es = 200000
epsuk = 0.07

# These factory functions create concrete and reinforcement materials according
# to the globally set design code
concrete = create_concrete(fck=fck)

carb_epsuk = 10*1**(-3)
carbon_reinforcement = create_reinforcement(fyk = 2200 ,ftk=2200, Es=220000, epsuk=carb_epsuk, density=1800, design_code='CFRP')
reinforcement = create_reinforcement(fyk=fyk, Es=Es, ftk=ftk, epsuk=epsuk)

# Create a rectangular hp_geometry
width = 250
height = 500
polygon = Polygon(
    [
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    ]
)  # We leverage shapely to create geometries
geometry = SurfaceGeometry(
    poly=polygon, material=concrete
)  # A SurfaceGeometry is a shapely Polygon with an assigned material

# Add reinforcement
diameter_reinf = 20
cover = 50

geometry = add_reinforcement(
    geometry,
    (
        -width / 2 + cover + diameter_reinf / 2,
        -height / 2 + cover + diameter_reinf / 2,
    ),
    diameter_reinf,
    reinforcement,
)  # The add_reinforcement function returns a CompoundGeometry
geometry = add_reinforcement(
    geometry,
    (
        width / 2 - cover - diameter_reinf / 2,
        -height / 2 + cover + diameter_reinf / 2,
    ),
    diameter_reinf,
    reinforcement,
)

# Create section
section = GenericSection(geometry)

# Calculate the moment-curvature response
moment_curvature = section.section_calculator.calculate_moment_curvature()
ult_m = section.section_calculator.calculate_bending_strength()

print(ult_m)
print(moment_curvature)
#
fig, ax = plt.subplots()
ax.plot(-moment_curvature.chi_y, -moment_curvature.m_y/1000/1000)
ax.set_xlabel("K [-]")
ax.set_ylabel("My [kNm]")

plt.show()





