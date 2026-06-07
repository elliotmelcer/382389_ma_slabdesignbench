"""Quickstart example."""

from shapely import Polygon

from structuralcodes import set_design_code
from structuralcodes.geometry import SurfaceGeometry, add_reinforcement
from structuralcodes.materials.concrete import create_concrete
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
print(carbon_reinforcement.constitutive_law)
carbon_reinforcement_2023 = create_reinforcement(fyk = 2200 ,ftk=2200, Es=220000, epsuk=carb_epsuk, density=1800, constitutive_law = 'elastic', name='CFRP')
reinforcement = create_reinforcement(fyk=fyk, Es=Es, ftk=ftk, epsuk=epsuk, density=7850)

# Create a rectangular hp_geometry
width = 200
height = 300
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
diameter_reinf = 3
cover = 50

geometry = add_reinforcement(
    geometry,
    (
        -width / 2 + cover + diameter_reinf / 2,
        -height / 2 + cover + diameter_reinf / 2,
    ),
    diameter_reinf,
    carbon_reinforcement,
)  # The add_reinforcement function returns a CompoundGeometry
geometry = add_reinforcement(
    geometry,
    (
        width / 2 - cover - diameter_reinf / 2,
        -height / 2 + cover + diameter_reinf / 2,
    ),
    diameter_reinf,
    carbon_reinforcement,
)
geometry = add_reinforcement(
    geometry,
    (
        0,
        -height / 2 + cover + diameter_reinf / 2,
    ),
    diameter_reinf,
    carbon_reinforcement,
)

# Create section
section = GenericSection(geometry)

# # Calculate the moment-curvature response
moment_curvature = section.section_calculator.calculate_moment_curvature()
ult_m = section.section_calculator.calculate_bending_strength()

print(ult_m)
print(moment_curvature)

for i, pg in enumerate(geometry.point_geometries, start=1):
    print(f"PointGeometry {i}: {pg.material.__class__}")

# Plot Moment-Curvature
moment_curvature.plot()

# Plot Cross-Section
geometry.plot(show=False)


# print(section.section_calculator.calculate_strain_profile(my=-2*10**6, nt=0, mz =0))

plt.show()








