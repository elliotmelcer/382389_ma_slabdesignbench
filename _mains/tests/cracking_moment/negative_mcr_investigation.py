from matplotlib import pyplot as plt
from structuralcodes import set_design_code
from structuralcodes.materials.reinforcement import create_reinforcement
from _mains.testing_files.testing_floor import test_floor
from _mains.testing_files.testing_loads import test_loads
from _mains.testing_files.testing_materials import infill, concrete_c30_uls, fyk_Q142, Es_Q142, ftk_Q142, epsuk_Q142, \
    brittle_elastic_law_Q142, density_Q142
from core.analysis_core.checks.structural_checks import DeflectionLimitByDeflectionCheckEC2004DE, \
    DeflectionLimitByMcrCheckEC2004DE
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm, calculate_bending_strength_uls_Nmm, \
    calculate_prestress_forces_Nmm, calculate_moment_curvature_sls, calculate_bending_strength_sls_Nmm
from core.analysis_core.statics.deformations import DeflectionCalculator
from core.analysis_core.statics.internal_forces import InternalForces
from core.visualization_core.visualization import plot_cross_section, plot_moment_curvature, plot_strain_profile
from slab_construction.slab_construction import SlabConstruction
from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
from slab_construction.slabs.hp_slab.model.hp_shell import HPShell
from slab_construction.slabs.hp_slab.model.hp_slab import HPSlab

set_design_code('ec2_2004')

solidian_Q142_pre_40 = create_reinforcement(
    fyk=fyk_Q142,
    Es=Es_Q142,
    ftk=ftk_Q142,
    epsuk=epsuk_Q142,
    density=density_Q142,
    constitutive_law = brittle_elastic_law_Q142,
    initial_strain = 0.400 * epsuk_Q142,
    gamma_s = 1.3,
    name = "solidian GRID Q142/142-CCE-25 prestressed 40%"
)

hp_shell = HPShell(HPGeometry(B=1520, L=7000, Hx=130, Hy=520, t=85, dy=190, nt=15), concrete_c30_uls, solidian_Q142_pre_40, reinf_area=100.5)

slab_construction = SlabConstruction(HPSlab(hp_shell, infill), test_floor)

section_midspan = slab_construction.slab.section_at(0.5)
section_support = slab_construction.slab.section_at(0.0)

# plot_cross_section(section_midspan)
# plot_cross_section(section_support)

mcr_results = calculate_cracking_moment_sls_Nmm(section_midspan)

m0_Nmm,_ = calculate_prestress_forces_Nmm(section_midspan)
m0_kNm = -m0_Nmm* 10 ** (-6)
m_cr_kNm = -mcr_results["m_cr"] * 10**(-6)
m_uk_kNm = -calculate_bending_strength_sls_Nmm(section_midspan)["m_u"] * 10 ** (-6)
m_ud_kNm = -calculate_bending_strength_uls_Nmm(section_midspan)["m_u"] * 10 ** (-6)
m_qp_kNm = InternalForces.calculate_moment_kNm(
    slab_construction,
    test_loads,
    system = "SIMPLE_BEAM",
    combination="QUASI-PERMANENT",
    moment_type="MAX_POS_MOMENT"
)

plot_strain_profile(mcr_results)

mk_results = calculate_moment_curvature_sls(section_midspan, constitutive_law="FCTM_PARABOLIC")

plot_moment_curvature(mk_results)

print("m0 = ", m0_kNm)
print("m_uk = ", m_uk_kNm)
print("m_ud = ", m_ud_kNm)
print("m_cr = ", m_cr_kNm)
print("m_qp = ", m_qp_kNm)

print("-" * 40)

util = DeflectionLimitByMcrCheckEC2004DE.calculateUtilization(
    slab_construction,
    test_loads,
    system = "SIMPLE_BEAM",
    moment = "MAX_POS_MOMENT",
    debug = True
    )

print(f"util = {util:.3f}")


plt.show()