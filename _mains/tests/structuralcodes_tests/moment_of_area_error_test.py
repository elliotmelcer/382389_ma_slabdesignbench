from matplotlib import pyplot as plt

from _mains.testing_files.testing_hp_sections import hp_section_c1_1_uls
from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm, sls_section
from core.visualization_core.visualization import plot_cross_section

def test_1_plot_sls_section() -> None:
    """
    Test 1: turns section into sls_section, then plot

    RUNS
    """
    print("test_1")
    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")

    plot_cross_section(sls_sec, x = 0.5)

    plt.show()

def test_2_get_section_from_results() -> None:
    """
    Test 2: get section from results

    FAILS

    Getting the section from results object breaks the code
     -> Bug must be within calculate_cracking_moment_sls()
    """
    print("test_2")

    results_c1_1 = calculate_cracking_moment_sls_Nmm(hp_section_c1_1_uls, n=0)

    plot_cross_section(results_c1_1.get("section"), x=0.5)

    plt.show()

def test_2_1_calculate_extents() -> None:
    """
    Idea 2.1: .calculate extents

    RUNS

    """

    print("test_2.2")
    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")

    sls_sec.geometry.calculate_extents()

    plot_cross_section(sls_sec, x = 0.5)

    plt.show()


def test_2_2_section_calculator() -> None:
    """
    Idea 2.2: calculator

    RUNS

    """

    print("test_2.2")
    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")

    calculator = sls_sec.section_calculator

    plot_cross_section(sls_sec, x=0.5)

    plt.show()

def test_2_3_integrate_strain_profile() -> None:
    """
    Idea 2.3: .integrate_strain_profile

    FAILS

    Running sls_sec.section_calculator.integrate_strain_profile breaks the code
    """
    print("test_2.1")


    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")

    strain_profile = [0.001, 0.001, 0.0]
    N_cr, My_cr, Mz_cr = sls_sec.section_calculator.integrate_strain_profile(
        strain=strain_profile,
        integrate='stress'
    )

    plot_cross_section(sls_sec, x=0.5)

    plt.show()


def test_2_4_integrate_strain_response_on_geometry() -> None:
    """
    Test: integrate_strain_response_on_geometry (the one used in bisection)

    RUNS
    """
    print("test_2.4")

    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")
    calculator = sls_sec.section_calculator

    # Simulate what happens in the bisection loop
    integration_data = getattr(calculator, 'integration_data', None)
    mesh_size = getattr(calculator, 'mesh_size', 0.01)

    N, My, Mz, integration_data = calculator.integrator.integrate_strain_response_on_geometry(
        sls_sec.geometry,
        [0.001, 0.001, 0.0],  # [eps_0, chi_y, chi_z]
        integration_data=integration_data,
        mesh_size=mesh_size
    )

    plot_cross_section(sls_sec, x=0.5)
    plt.show()


def test_2_5_multiple_integrations() -> None:
    """
    Test: multiple integration calls (like in bisection)

    RUNS
    """
    print("test_2.5")

    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")
    calculator = sls_sec.section_calculator

    integration_data = None
    mesh_size = 0.01

    # Call it 10 times like the bisection does
    for i in range(10):
        N, My, Mz, integration_data = calculator.integrator.integrate_strain_response_on_geometry(
            sls_sec.geometry,
            [0.001 * (i + 1), 0.001, 0.0],
            integration_data=integration_data,
            mesh_size=mesh_size
        )

    plot_cross_section(sls_sec, x=0.5)
    plt.show()


def test_2_6_integrate_strain_profile_different_params() -> None:
    """
    Test: Does the integrate parameter matter?

    FAILS

    It'S not because of specific parameters in .integrate_strain_profile()
    """
    print("test_2.6")

    sls_sec = sls_section(hp_section_c1_1_uls, "FCTM_PARABOLIC")

    # Try without the integrate parameter (if it has a default)
    try:
        N_cr, My_cr, Mz_cr = sls_sec.section_calculator.integrate_strain_profile(
            strain=[0.001, 0.001, 0.0]
            # No integrate='stress'
        )
    except:
        print("Failed without integrate parameter")

    plot_cross_section(sls_sec, x=0.5)
    plt.show()

def test_3_calculate_bending_strength() -> None:
    """
    Idea 3: calculate_bending_strength_uls() also FAILS. Lets check calculate_bending_strength()

    FAILS

    """
    print("test_2.1")


    # hp_section_c1_1_uls.section_calculator.calculate_bending_strength(n=0)

    plot_cross_section(hp_section_c1_1_uls, x=0.5)

    plt.show()

def test_4_clear_integration_data() -> None:
    print("test_2.1")

    hp_section_c1_1_uls.section_calculator.calculate_bending_strength(n=0)

    # Clear the integration cache
    if hasattr(hp_section_c1_1_uls.section_calculator, 'integration_data'):
        hp_section_c1_1_uls.section_calculator.integration_data = None

    plot_cross_section(hp_section_c1_1_uls, x=0.5)
    plt.show()

if __name__ == '__main__':
    # test_1_plot_sls_section()
    # test_2_get_section_from_results()
    # test_2_1_calculate_extents()
    # test_2_2_section_calculator()
    # test_2_3_integrate_strain_profile()
    # test_2_4_integrate_strain_response_on_geometry()
    # test_2_5_multiple_integrations()
    # test_2_6_integrate_strain_profile_different_params()
    # test_3_calculate_bending_strength()
    test_4_clear_integration_data()

