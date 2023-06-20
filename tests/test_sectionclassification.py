""" Tests for the sectionclassification module
"""

from pytest import fixture, raises, approx
import eurocodedesign.standard.ec3.sectionclassification as sc
import eurocodedesign.geometry.steelsections as sec
import eurocodedesign.materials.structuralsteel as stl


@fixture
def S235_thin_material():
    return stl.S235()


@fixture
def S355_thin_material():
    return stl.S355()


@fixture
def ipe240():
    return sec.get("IPE240")


@fixture
def ipe270():
    return sec.get("IPE270")


@fixture
def ipe330():
    return sec.get("IPE330")


@fixture
def hea300():
    return sec.get("HEA300")


@fixture
def chs219x6():
    return sec.get("CHS219.1x6")


@fixture
def chs323x6():
    return sec.get("CHS323.9x6")


@fixture
def chs355x5():
    return sec.get("CHS355.6x5")


@fixture
def shs140x4():
    return sec.get("SHS140x4")


@fixture
def shs120x3():
    return sec.get("SHS120x3")


class TestBoundaryValuesForDoubleSupportedElements:
    def test_class_one_with_alpha_lt_half(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.4, 1.0, 1)
        assert ct_bound == approx(90)

    def test_class_one_with_alpha_eq_half(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.5, 1.0, 1)
        assert ct_bound == approx(72)

    def test_class_one_with_alpha_eq_one(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(1.0, 1.0, 1)
        assert ct_bound == approx(33)

    def test_class_one_with_alpha_gt_half_and_epsilon(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.6, 0.81, 1)
        assert ct_bound == approx(47.1705882)

    def test_class_one_with_alpha_lt_half_and_epsilon(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.4, 0.81, 1)
        assert ct_bound == approx(72.9)

    def test_class_two_with_alpha_lt_half(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.4, 1.0, 2)
        assert ct_bound == approx(103.75)

    def test_class_two_with_alpha_eq_half(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.5, 1.0, 2)
        assert ct_bound == approx(83)

    def test_class_two_w_alpha_eq_one(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(1.0, 1.0, 2)
        assert ct_bound == approx(38)

    def test_class_two_with_alpha_gt_half_and_epsilon(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.6, 0.81, 2)
        assert ct_bound == approx(54.317647)

    def test_class_two_with_alpha_lt_half_and_epsilon(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(0.4, 0.81, 2)
        assert ct_bound == approx(84.0375)

    def test_class_three_with_psi_gt_negative_one(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(-0.5, 1.0, 3)
        assert ct_bound == approx(83.1683168)

    def test_class_three_with_psi_lt_negative_one(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(-1.5, 1.0, 3)
        assert ct_bound == approx(189.835455)

    def test_class_three_with_psi_eq_negative_one_and_epsilon(self):
        ct_bound = sc._boundary_ct_for_double_supported_elements(-1.0, 0.81, 3)
        assert ct_bound == approx(100.44)

    def test_invalid_section_class(self):
        with raises(ValueError, match="Invalid section class: '5'"):
            sc._boundary_ct_for_double_supported_elements(-1.0, 0.81, 5)


class TestAlphaForMajorAxisSymmetricSections:
    def test_no_normal_force(self, ipe270, S235_thin_material):
        normal_force = 0
        expected = (219.6 / 2 + 0 / 2) / 219.6
        actual = sc._alpha_for_major_axis_symmetric_sections(
            ipe270, S235_thin_material, normal_force, ipe270.root_radius
        )
        assert actual == approx(expected)

    def test_maximum_normal_force(self, ipe270, S235_thin_material):
        normal_force = 340_599.6  # maximum plastic capacity of web tw*hw*f_yk
        expected = (219.6 / 2 + 219.6 / 2) / 219.6
        actual = sc._alpha_for_major_axis_symmetric_sections(
            ipe270, S235_thin_material, normal_force, ipe270.root_radius
        )
        assert actual == approx(expected)

    def test_arbitrary_normal_force(self, ipe270, S235_thin_material):
        normal_force = 100_000  # maximum plastic capacity of web tw*hw*f_yk
        expected = (219.6 / 2 + 64.4745326 / 2) / 219.6
        actual = sc._alpha_for_major_axis_symmetric_sections(
            ipe270, S235_thin_material, normal_force, ipe270.root_radius
        )
        assert actual == approx(expected)

    def test_normal_force_gt_web_capacity(self, ipe270, S235_thin_material):
        normal_force = 525_000  # 101% of shear area
        actual = sc._alpha_for_major_axis_symmetric_sections(
            ipe270, S235_thin_material, normal_force, ipe270.root_radius
        )
        assert actual == 1.0


class TestPsiForMajorAxisSymmetricSections:
    _normal_force = 1_000_000  # N - compression
    _bending_moment = 150_000_000  # Nm - compression in top flange

    def test_psi_gt_minus1(self, hea300):
        actual = sc._psi_for_major_axis_symmetric_sections(
            self._normal_force, self._bending_moment, hea300
        )
        assert actual == approx(-0.145168551)

    def test_psi_lt_minus1(self, hea300):
        # -ve normal force for tension
        actual = sc._psi_for_major_axis_symmetric_sections(
            -self._normal_force, self._bending_moment, hea300
        )
        assert actual == approx(-6.888544317)


def test_normal_stress():
    assert sc.normal_stress(100_000, 5000) == 20


def test_bending_stress():
    assert sc.bending_stress(100_000, 5000) == 20


def test_c_web_for_symmetric_I_section(ipe270):
    c_web = sc._c_web_for_symmetric_I_section(ipe270, ipe270.root_radius)
    assert c_web == 219.6


def test_e_from_normal_force(ipe270, S235_thin_material):
    e = sc._e_from_normal_force(ipe270, S235_thin_material, 100_000, 1.0)
    assert e == approx(100_000 * 1.0 / 6.6 / S235_thin_material.f_yk)


class TestBoundaryValuesForSingleSupportedElements:
    def test_class_one(self):
        ct_bound = sc._boundary_ct_for_single_supported_elements(0.81, 1)
        assert ct_bound == approx(7.29)

    def test_class_two(self):
        ct_bound = sc._boundary_ct_for_single_supported_elements(1, 2)
        assert ct_bound == approx(10)

    def test_class_three(self):
        ct_bound = sc._boundary_ct_for_single_supported_elements(0.6, 3)
        assert ct_bound == approx(8.4)


class TestSectionSpecificClassificationParameters:
    # todo
    def test_shs_parameters(self):
        actual = sc._rhs_shs_i_section_classification(shs140x4)
    pass
    
    
class TestRhsShsISectionClassification:
    # todo
    pass
    

class TestSectionClassification:
    # todo
    pass    
# class TestRolledISectionClassification:
#     def test_class_one(self, S235_thin_material, ipe240):
#         # no compression force only moment
#         actual = sc._rolled_I_section_classification(
#             ipe240, S235_thin_material, 0.0, 150_000_000
#         )
#         assert actual == 1

#     def test_class_two(self, S235_thin_material, ipe270):
#         # compression 99% of the web capacity
#         actual = sc._rolled_I_section_classification(
#             ipe270, S235_thin_material, 514_000, 0.0
#         )
#         assert actual == 2

#     def test_class_three(self, S355_thin_material, ipe270):
#         # compression 99% of the web capacity
#         actual = sc._rolled_I_section_classification(
#             ipe270, S355_thin_material, 775_000, 0.0
#         )
#         assert actual == 3

#     def test_class_four(self, S355_thin_material, ipe330):
#         # compression 99% of the web capacity
#         actual = sc._rolled_I_section_classification(
#             ipe330, S355_thin_material, 1_082_000, 0.0
#         )
#         assert actual == 4


class TestCircularHollowSectionClassification:
    def test_class_one(self, S235_thin_material, chs219x6):
        actual = sc._chs_section_classification(chs219x6, S235_thin_material)
        assert actual == 1

    def test_class_two(self, S235_thin_material, chs323x6):
        actual = sc._chs_section_classification(chs323x6, S235_thin_material)
        assert actual == 2

    def test_class_three(self, S355_thin_material, chs323x6):
        actual = sc._chs_section_classification(chs323x6, S355_thin_material)
        assert actual == 3

    def test_class_four(self, S355_thin_material, chs355x5):
        actual = sc._chs_section_classification(chs355x5, S355_thin_material)
        assert actual == 4


# class TestRectangularAndSquareHollowSectionClassification:
#     def test_class_one(self, S235_thin_material, shs140x4):
#         actual = sc._rhs_shs_section_classification(
#             shs140x4, S235_thin_material, 0.0, 20_000_000
#         )
#         assert actual == 1

#     def test_class_two(self, S235_thin_material, shs120x3):
#         actual = sc._rhs_shs_section_classification(
#             shs120x3, S235_thin_material, 500_000, 0.0
#         )
#         assert actual == 2

#     def test_class_three(self, S355_thin_material, shs140x4):
#         actual = sc._rhs_shs_section_classification(
#             shs140x4, S355_thin_material, 500_000, 0.0
#         )
#         assert actual == 3

#     def test_class_four(self, S355_thin_material, shs120x3):
#         actual = sc._rhs_shs_section_classification(
#             shs120x3, S355_thin_material, 500_000, 0.0
#         )
#         assert actual == 4
