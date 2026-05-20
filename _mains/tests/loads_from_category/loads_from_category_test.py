from _mains.testing_files.testing_slab_construction import test_slab_construction_c1_4
from core.analysis_core.statics.loads import Loads


def loads_from_category_test():
    print("\n=== LOADS FROM CATEGORY TEST ===")

    # --- Input validation ---
    try:
        Loads.from_categories_EC0_NA_DE("Z9")
        print("ERROR: should have raised ValueError for 'Z9'")
    except ValueError as e:
        print(f"Correctly raised ValueError for 'Z9': {e}")

    try:
        Loads.from_categories_EC0_NA_DE("A9")
        print("ERROR: should have raised ValueError for 'A9'")
    except ValueError as e:
        print(f"Correctly raised ValueError for 'A9': {e}")

    # --- Single load ---
    loads_single = Loads.from_categories_EC0_NA_DE("A1")
    print(f"\nSingle category 'A1':")
    print(f"  Qk:    {loads_single.Qk}")
    print(f"  psi_0: {loads_single.psi_0_values}")
    print(f"  psi_1: {loads_single.psi_1_values}")
    print(f"  psi_2: {loads_single.psi_2_values}")

    print(f"\n  Fundamental (ULS):      {loads_single.fundamental_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")
    print(f"  Frequent (SLS):         {loads_single.frequent_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")
    print(f"  Quasi-permanent (SLS):  {loads_single.quasi_permanent_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")

    # --- Multiple loads (A1 leading, B2 accompanying) ---
    loads_multi = Loads.from_categories_EC0_NA_DE(["A1", "B2"])
    print(f"\nMultiple categories ['A1', 'B2'] — A1 is leading:")
    print(f"  Qk:    {loads_multi.Qk}")
    print(f"  psi_0: {loads_multi.psi_0_values}")
    print(f"  psi_1: {loads_multi.psi_1_values}")
    print(f"  psi_2: {loads_multi.psi_2_values}")

    print(f"\n  Fundamental (ULS):      {loads_multi.fundamental_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")
    print(f"  Frequent (SLS):         {loads_multi.frequent_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")
    print(f"  Quasi-permanent (SLS):  {loads_multi.quasi_permanent_combination_kN_m2_EC0(test_slab_construction_c1_4):.2f} kN/m²")

if __name__ == "__main__":
    loads_from_category_test()