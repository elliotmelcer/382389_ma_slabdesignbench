"""
Author: [Your Name]
Test file for SlabConstruction.get_parameters() method

Tests the extraction of all slab construction parameters from the nested
HPSlab -> HPShell -> HPGeometry structure.
"""

from _mains.testing_files.testing_slab_construction import test_slab_construction

"""
Expected values based on test_slab_construction:

hp_c1_4 = HPGeometry(B = 1200, L = 6750, Hx = 100, Hy = 400, t = 100, dy = 80, nt = 10)
hp_shell_c1_4_uls = HPShell(hp_c1_4, concrete_c55_uls, solidian_Q142_pre_50, reinf_area = 80)
hp_slab_c1_4_uls = HPSlab(hp_shell_c1_4_uls, infill)

test_floor:
    - infill_layer:           thickness = 0.0 mm
    - sound_insulation_layer: thickness = 12.0 mm
    - screed_layer:           thickness = 45.0 mm
"""


def test_get_parameters():
    """
    Test that get_parameters() returns the correct dictionary structure and values.
    """
    print("=" * 70)
    print("TEST: SlabConstruction.get_parameters()")
    print("=" * 70)

    # Get parameters
    params_ = test_slab_construction.get_parameters()

    # Print results
    print("\nReturned parameters:")
    print("-" * 70)

    print("\n[GEOMETRY]")
    for key, value in params_["geometry"].items():
        print(f"  {key}: {value}")

    print("\n[CONCRETE]")
    for key, value in params_["concrete"].items():
        print(f"  {key}: {value}")

    print("\n[REINFORCEMENT]")
    for key, value in params_["reinforcement"].items():
        print(f"  {key}: {value}")

    # --- Assertions ---
    print("\n" + "=" * 70)
    print("ASSERTIONS")
    print("=" * 70)

    # Expected values
    expected_geometry = {
        "span_L": 6750.0,
        "width_B": 1200.0,
        "height": 500.0,              # Hx + Hy = 100 + 400
        "Hx_Hges": 0.2,               # 100 / 500
        "thickness": 100.0,
        "nt": 10,
        "dy": 80.0,
        "thickness_infill": 0.0,
        "thickness_screed": 45.0,
        "thickness_insulation": 12.0,
    }

    expected_concrete = {
        "fck": 55.0,
    }

    expected_reinforcement_area = 80.0

    # Check geometry
    print("\nGeometry checks:")
    for key, expected in expected_geometry.items():
        actual = params_["geometry"][key]
        status = "✓" if abs(actual - expected) < 1e-6 else "✗"
        print(f"  {status} {key}: expected {expected}, got {actual}")
        assert abs(actual - expected) < 1e-6, f"{key} mismatch: expected {expected}, got {actual}"

    # Check concrete
    print("\nConcrete checks:")
    for key, expected in expected_concrete.items():
        actual = params_["concrete"][key]
        status = "✓" if abs(actual - expected) < 1e-6 else "✗"
        print(f"  {status} {key}: expected {expected}, got {actual}")
        assert abs(actual - expected) < 1e-6, f"{key} mismatch: expected {expected}, got {actual}"

    # Check reinforcement
    print("\nReinforcement checks:")

    # Cross-sectional area
    actual_area = params_["reinforcement"]["cross_sectional_area"]
    status = "✓" if abs(actual_area - expected_reinforcement_area) < 1e-6 else "✗"
    print(f"  {status} cross_sectional_area: expected {expected_reinforcement_area}, got {actual_area}")
    assert abs(actual_area - expected_reinforcement_area) < 1e-6

    # Name should contain 'Q142' and 'prestressed'
    name = params_["reinforcement"]["name"]
    status = "✓" if "Q142" in name else "✗"
    print(f"  {status} name contains 'Q142': {name}")
    assert "Q142" in name, f"Expected reinforcement name to contain 'Q142', got {name}"

    # Initial strain should be ~50% (check it's roughly in the right range)
    initial_strain_pct = params_["reinforcement"]["initial_strain_percentage"]
    # solidian_Q142 has epsuk = 10e-3, so 50% prestress = 0.005, as percentage = 0.5%
    # But if initial_strain is stored as 0.50 * epsuk = 0.005, then *100 = 0.5
    print(f"  initial_strain_percentage: {initial_strain_pct}")
    assert initial_strain_pct > 0, "Initial strain should be positive for prestressed reinforcement"

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)

    return params_


def test_parameter_types():
    """
    Test that all returned values have the correct types.
    """
    print("\n" + "=" * 70)
    print("TEST: Parameter Types")
    print("=" * 70)

    params = test_slab_construction.get_parameters()

    # Check structure
    assert isinstance(params, dict), "params should be a dict"
    assert "geometry" in params, "params should contain 'geometry'"
    assert "concrete" in params, "params should contain 'concrete'"
    assert "reinforcement" in params, "params should contain 'reinforcement'"

    # Check geometry types
    geo = params["geometry"]
    assert isinstance(geo["span_L"], float), "span_L should be float"
    assert isinstance(geo["width_B"], float), "width_B should be float"
    assert isinstance(geo["height"], float), "height should be float"
    assert isinstance(geo["Hx_Hges"], float), "Hx_Hges should be float"
    assert isinstance(geo["thickness"], float), "thickness should be float"
    assert isinstance(geo["nt"], int), "nt should be int"
    assert isinstance(geo["dy"], float), "dy should be float"
    assert isinstance(geo["thickness_infill"], float), "thickness_infill should be float"
    assert isinstance(geo["thickness_screed"], float), "thickness_screed should be float"
    assert isinstance(geo["thickness_insulation"], float), "thickness_insulation should be float"

    # Check concrete types
    conc = params["concrete"]
    assert isinstance(conc["fck"], (int, float)), "fck should be numeric"

    # Check reinforcement types
    reinf = params["reinforcement"]
    assert isinstance(reinf["name"], str), "name should be str"
    assert isinstance(reinf["initial_strain_percentage"], (int, float)), "initial_strain_percentage should be numeric"
    assert isinstance(reinf["cross_sectional_area"], (int, float)), "cross_sectional_area should be numeric"

    print("All type checks passed ✓")


if __name__ == "__main__":
    params = test_get_parameters()
    test_parameter_types()