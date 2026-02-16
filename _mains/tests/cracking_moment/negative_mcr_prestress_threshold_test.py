from core.analysis_core.section_methods import calculate_cracking_moment_sls_Nmm

if __name__ == "__main__":
    from structuralcodes import set_design_code
    from structuralcodes.materials.concrete import create_concrete
    from structuralcodes.materials.reinforcement import create_reinforcement
    from structuralcodes.materials.constitutive_laws import Elastic

    from slab_construction.slabs.hp_slab.model.hp_geometry import HPGeometry
    from slab_construction.slabs.hp_slab.model.hp_shell import HPShell

    set_design_code('ec2_2004')


    def test_prestress_level(prestress_factor: float):
        """Test the fixed function at a given prestress level."""

        # Create section (same parameters as before)
        span_L, width_B, height = 7000.0, 1520.0, 650.0
        Hx_Hges, thickness, nt, dy = 0.2, 85.0, 15, 190.0
        fck, reinf_area = 30.0, 100.5

        Hx = Hx_Hges * height
        Hy = (1 - Hx_Hges) * height

        concrete = create_concrete(
            fck=fck, constitutive_law='parabolarectangle',
            alpha_cc=0.85, gamma_c=1.5
        )

        epsuk = 0.01
        brittle_elastic = Elastic(220000, eps_u=epsuk)
        reinforcement = create_reinforcement(
            fyk=2200, Es=220000, ftk=2200, epsuk=epsuk,
            density=1800, constitutive_law=brittle_elastic,
            initial_strain=prestress_factor * epsuk, gamma_s=1.3
        )

        hp_geom = HPGeometry(B=width_B, L=span_L, Hx=Hx, Hy=Hy, t=thickness, dy=dy, nt=nt)
        hp_shell = HPShell(hp_geom, concrete, reinforcement, reinf_area=reinf_area)
        section = hp_shell.section_at(0.5)

        # Test the fixed function
        result = calculate_cracking_moment_sls_Nmm(section, n=0)

        m_cr_kNm = result['m_cr'] / 1e6 if result['valid'] else float('-inf')

        return {
            'factor': prestress_factor,
            'valid': result['valid'],
            'm_cr': m_cr_kNm,
            'reason': result.get('reason'),
        }


    # Test across the threshold
    print("=" * 70)
    print("TESTING FIXED calculate_cracking_moment_sls")
    print("=" * 70)

    test_factors = [0.35, 0.38, 0.39, 0.392, 0.393, 0.40, 0.45, 0.50]

    print(f"\n{'Factor':<10} {'Valid':<8} {'m_cr [kNm]':<15} {'Reason'}")
    print("-" * 70)

    for f in test_factors:
        r = test_prestress_level(f)
        m_cr_str = f"{r['m_cr']:.2f}" if r['valid'] else "-inf"
        reason_str = r['reason'] if r['reason'] else ""
        print(f"{f:<10.3f} {str(r['valid']):<8} {m_cr_str:<15} {reason_str[:40]}")

    print("\n" + "=" * 70)
    print("Expected behavior:")
    print("  - Prestress ≤ ~39.2%: Valid solution with m_cr ≈ -760 kNm")
    print("  - Prestress > ~39.2%: Invalid (returns -inf), section crushes before cracking")
    print("=" * 70)