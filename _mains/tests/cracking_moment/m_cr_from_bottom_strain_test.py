from _mains.testing_files.testing_hp_sections import (
    hp_section_c1_4_uls,
    hp_section_c1_3_uls,
    hp_section_c1_2_c50_uls,
    hp_section_c1_2_c80_uls,
    hp_section_c1_1_uls,
)
from core.analysis_core.section_methods import (
    calculate_simplified_moment_curvature_sls,
    calculate_cracking_moment_sls_Nmm,
    sls_section,
    get_concrete,
    calculate_section_state_from_bottom_strain_sls,
)

"""
This test demonstrates the new method for calculating the cracking moment: 

calculate_curvature_from_bottom_strain_sls_Nmm

Output (18.03.2026):

m_cr [kNm]
Section           Original         New    Diff (%)
--------------------------------------------------
c1_1               -37.531     -37.531       -0.00%
c1_2_c50          -185.098    -185.098       -0.00%
c1_2_c80          -192.822    -192.822        0.00%
c1_3               -46.344     -46.344        0.00%
c1_4              -409.734    -409.734       -0.00%

kappa_cr [1/m * 1e3]
Section           Original         New    Diff (%)
--------------------------------------------------
c1_1             -0.004233   -0.004233       -0.00%
c1_2_c50         -0.002933   -0.002933       -0.00%
c1_2_c80         -0.002639   -0.002639        0.00%
c1_3             -0.000517   -0.000517        0.00%
c1_4             -0.002068   -0.002068       -0.00%


Conclusion:
New method can be used to determine cracking moment as well. 

"""
sections = {
    "c1_1": hp_section_c1_1_uls,
    "c1_2_c50": hp_section_c1_2_c50_uls,
    "c1_2_c80": hp_section_c1_2_c80_uls,
    "c1_3": hp_section_c1_3_uls,
    "c1_4": hp_section_c1_4_uls,
}

results = {}
for name, section in sections.items():
    current_sls_section = sls_section(section, concrete_tension=True, tension_stiffening=True)

    m_cr_result_original = calculate_cracking_moment_sls_Nmm(section)
    m_cr_original = m_cr_result_original["m_cr"]
    _, kappa_cr_original, _ = m_cr_result_original["strain_profile"]

    concrete_sls = get_concrete(current_sls_section)
    eps_cr = concrete_sls.fctm / concrete_sls.Ecm
    m_cr_result_from_strain = calculate_section_state_from_bottom_strain_sls(current_sls_section, eps_cr)
    m_cr_from_strain = m_cr_result_from_strain["m_y"]
    _,kappa_cr_from_strain,_ = m_cr_result_from_strain["strain_profile"]

    results[name] = {
        "m_orig":  m_cr_original    / 1e6,
        "m_new":   m_cr_from_strain / 1e6,
        "k_orig":  kappa_cr_original    * 1000,
        "k_new":   kappa_cr_from_strain * 1000,
    }

col = 12
header = f"{'Section':<14}" + f"{'Original':>{col}}" + f"{'New':>{col}}" + f"{'Diff (%)':>{col}}"
divider = "-" * len(header)

print("m_cr [kNm]")
print(header)
print(divider)
for name, r in results.items():
    diff = (r["m_new"] - r["m_orig"]) / r["m_orig"] * 100
    print(f"{name:<14}{r['m_orig']:>{col}.3f}{r['m_new']:>{col}.3f}{diff:>{col}.2f}%")

print()
print("kappa_cr [mm/m]")
print(header)
print(divider)
for name, r in results.items():
    diff = (r["k_new"] - r["k_orig"]) / r["k_orig"] * 100
    print(f"{name:<14}{r['k_orig']:>{col}.6f}{r['k_new']:>{col}.6f}{diff:>{col}.2f}%")