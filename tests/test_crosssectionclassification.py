""" Tests for the sectionclassification module
"""

from pytest import fixture, raises, approx
from eurocodedesign.units import Pascal, MPa, mm
import eurocodedesign.standard.ec3.crosssectionclassification as csc
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


class TestClassifyDsupElement:
    def test_355MPa_default_values_class_4(self):
        actual = csc.classify_dsup_element(mm(550), mm(10), MPa(355))
        expected = 4
        assert actual == expected

    def test_355MPa_default_values_class_3(self):
        actual = csc.classify_dsup_element(mm(330), mm(10), MPa(355))
        expected = 3
        assert actual == expected

    def test_355MPa_default_values_class_2(self):
        actual = csc.classify_dsup_element(mm(290), mm(10), MPa(355))
        expected = 2
        assert actual == expected

    def test_355MPa_default_values_class_1(self):
        actual = csc.classify_dsup_element(mm(250), mm(10), MPa(355))
        expected = 1
        assert actual == expected

    def test_235MPa_user_defined_alpha_value(self):
        with raises(
            ValueError,
            match=r"The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'.",
        ):
            csc.classify_dsup_element(mm(250), mm(10), MPa(235), alpha=0.5)

    def test_235MPa_user_defined_psi_value(self):
        with raises(
            ValueError,
            match=r"The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'.",
        ):
            csc.classify_dsup_element(mm(250), mm(10), MPa(235), psi=0.5)

    def test_235MPa_user_defined_alpha_and_psi_values_class1(self):
        actual = csc.classify_dsup_element(
            mm(250), mm(10), MPa(235), alpha=0.5, psi=0.5
        )
        expected = 1
        assert actual == expected


class TestCtLimitsDsupElements:
    def test_235MPa_pure_bending(self):
        actual = csc.ct_limits_dsup_elements(MPa(235), 0.5, -1)
        expected = {1: 72, 2: 83, 3: 124}
        assert actual == expected

    def test_235MPa_pure_compression(self):
        actual = csc.ct_limits_dsup_elements(MPa(235), 1, 1)
        expected = {1: 33, 2: 38, 3: 42}
        assert actual == expected

    def test_235MPa_bending_and_compression(self):
        actual = csc.ct_limits_dsup_elements(MPa(235), 0.3, -1.3)
        expected = {1: 120, 2: 138.3333333, 3: 162.5890156}
        assert actual == approx(expected)


class TestCtLimitsDsupElementClassOne:
    def test_alpha_lt_half(self):
        actual = csc.ct_limit_dsup_element_class_1(MPa(235), 0.4)
        expected = 90
        assert actual == expected

    def test_alpha_eq_half(self):
        actual = csc.ct_limit_dsup_element_class_1(MPa(355), 0.5)
        expected = 0.8136165135 * 72
        assert actual == approx(expected)

    def test_alpha_gt_half(self):
        actual = csc.ct_limit_dsup_element_class_1(MPa(355), 0.6)
        expected = 0.8136165135 * 58.23529412
        assert actual == approx(expected)


class TestCtLimitsDsupElementClassTwo:
    def test_alpha_lt_half(self):
        actual = csc.ct_limit_dsup_element_class_2(MPa(235), 0.4)
        expected = 103.75
        assert actual == approx(expected)

    def test_alpha_eq_half(self):
        actual = csc.ct_limit_dsup_element_class_2(MPa(355), 0.5)
        expected = 0.8136165135 * 83
        assert actual == approx(expected)

    def test_alpha_gt_half(self):
        actual = csc.ct_limit_dsup_element_class_2(MPa(355), 0.6)
        expected = 0.8136165135 * 67.05882353
        assert actual == approx(expected)


class TestCtLimitsDsupElementClassThree:
    def test_psi_lt_minus_one(self):
        actual = csc.ct_limit_dsup_element_class_3(MPa(235), -1.1)
        expected = 136.554912
        assert actual == approx(expected)

    def test_psi_eq_minus_one(self):
        actual = csc.ct_limit_dsup_element_class_3(MPa(235), -1.0)
        expected = 124
        assert actual == approx(expected)

    def test_psi_gt_minus_one(self):
        actual = csc.ct_limit_dsup_element_class_3(MPa(275), -0.9)
        expected = 0.9244162777 * 112.6005362
        assert actual == approx(expected)


class TestClassifySsupElement:
    def test_default_values_class_one(self):
        actual = csc.classify_ssup_element(mm(80), mm(10), MPa(235))
        expected = 1
        assert actual == expected

    def test_default_values_class_two(self):
        actual = csc.classify_ssup_element(mm(95), mm(10), MPa(235))
        expected = 2
        assert actual == expected

    def test_default_values_class_three(self):
        actual = csc.classify_ssup_element(mm(130), mm(10), MPa(235))
        expected = 3
        assert actual == expected

    def test_default_values_class_four(self):
        actual = csc.classify_ssup_element(mm(170), mm(10), MPa(235))
        expected = 4
        assert actual == expected

    def test_235MPa_user_defined_alpha_value(self):
        with raises(
            ValueError,
            match=r"The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'.",
        ):
            csc.classify_ssup_element(mm(250), mm(10), MPa(235), alpha=0.5)

    def test_235MPa_user_defined_psi_value(self):
        with raises(
            ValueError,
            match=r"The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'.",
        ):
            csc.classify_ssup_element(mm(250), mm(10), MPa(235), psi=0.5)

    def test_235MPa_user_defined_alpha_and_psi_values_class3(self):
        actual = csc.classify_ssup_element(
            mm(205), mm(10), MPa(235), alpha=0.5, psi=-1.4
        )
        expected = 3
        assert actual == expected

    def test_235MPa_tension_free_edge_default_alpha_and_psi_class2(self):
        actual = csc.classify_ssup_element(
            mm(95), mm(10), MPa(235), comp_free_edge=False
        )
        expected = 2
        assert actual == expected

    def test_355MPa_tension_free_edge_user_alpha_and_psi_class1(self):
        actual = csc.classify_ssup_element(
            mm(200), mm(10), MPa(355), alpha=0.5, psi=-1, comp_free_edge=False
        )
        expected = 1
        assert actual == expected


class TestCtLimitsSsupElements:
    def test_pure_compression(self):
        actual = csc.ct_limits_ssup_elements(MPa(235), 1.0, 1.0)
        expected = {1: 9.0, 2: 10.0, 3: 14.0}
        assert actual == approx(expected)

    def test_compression_free_edge(self):
        actual = csc.ct_limits_ssup_elements(MPa(235), 0.5, -1.0)
        expected = {1: 18.0, 2: 20.0, 3: 19.36104336}
        assert actual == approx(expected)

    def test_tension_free_edge(self):
        actual = csc.ct_limits_ssup_elements(MPa(235), 0.5, -1.0, comp_free_edge=False)
        expected = {1: 25.45584412, 2: 28.28427125, 3: 102.4490117}
        assert actual == approx(expected)


class TestCtLimitSsupElementClassOne:
    def test_275MPa_alpha_eq_one(self):
        actual = csc.ct_limit_ssup_element_class_1(MPa(275), 1.0)
        expected = 0.9244162777 * 9
        assert actual == approx(expected)

    def test_355MPa_alpha_neq_one(self):
        actual = csc.ct_limit_ssup_element_class_1(MPa(355), 0.5)
        expected = 0.8136165135 * 9 / 0.5
        assert actual == approx(expected)


class TestCtLimitSsupElementClassTwo:
    def test_275MPa_alpha_eq_one(self):
        actual = csc.ct_limit_ssup_element_class_2(MPa(275), 1.0)
        expected = 0.9244162777 * 10
        assert actual == approx(expected)

    def test_355MPa_alpha_neq_one(self):
        actual = csc.ct_limit_ssup_element_class_2(MPa(355), 0.5)
        expected = 0.8136165135 * 10 / 0.5
        assert actual == approx(expected)


class TestCtLimitSsupElementClassThree:
    def test_275MPa_psi_eq_one(self):
        actual = csc.ct_limit_ssup_element_class_3(MPa(275), 1.0)
        expected = 0.9244162777 * 14.0
        assert actual == approx(expected)

    def test_355MPa_psi_neq_one(self):
        actual = csc.ct_limit_ssup_element_class_3(MPa(355), 0.0)
        expected = 0.8136165135 * 21 * 0.7549834435
        assert actual == approx(expected)


class TestCalcKsigma:
    def test_compression_free_edge(self):
        actual = csc.calc_k_sigma(0.5)
        expected = 0.4825
        assert actual == approx(expected)

    def test_tension_free_edge_gt_zero(self):
        actual = csc.calc_k_sigma(0.5, comp_free_edge=False)
        expected = 0.6880952381
        assert actual == approx(expected)

    def test_tension_free_edge_eq_zero(self):
        actual = csc.calc_k_sigma(0.0, comp_free_edge=False)
        expected = 1.7
        assert actual == approx(expected)

    def test_tension_free_edge_eq_one(self):
        actual = csc.calc_k_sigma(1.0, comp_free_edge=False)
        expected = 0.43
        assert actual == approx(expected)

    def test_tension_free_edge_eq_minus_one(self):
        actual = csc.calc_k_sigma(-1, comp_free_edge=False)
        expected = 23.8
        assert actual == approx(expected)


class TestTensionFreeEdgeClassification:
    def test_class_one(self):
        actual = csc.ct_limit_ssup_element_class_1_tension_free_edge(MPa(235), 0.5)
        expected = 25.45584412
        assert actual == approx(expected)

    def test_class_two(self):
        actual = csc.ct_limit_ssup_element_class_2_tension_free_edge(MPa(235), 0.5)
        expected = 28.28427125
        assert actual == approx(expected)

    def test_class_two(self):
        actual = csc.ct_limit_ssup_element_class_3_tension_free_edge(MPa(235), -1.0)
        expected = 102.4490117
        assert actual == approx(expected)


class TestClassifyChsCrossSection():
    def test_235MPa_class_one(self):
        actual = csc.classify_chs_cross_section(mm(450), mm(10), MPa(235))
        expected = 1
        assert actual == expected
        
    def test_355MPa_class_two(self):
        actual = csc.classify_chs_cross_section(mm(400), mm(10), MPa(355))
        expected = 2
        assert actual == expected
        
    def test_355MPa_class_three(self):
        actual = csc.classify_chs_cross_section(mm(550), mm(10), MPa(355))
        expected = 3
        assert actual == expected
        
    def test_355MPa_class_four(self):
        actual = csc.classify_chs_cross_section(mm(650), mm(10), MPa(355))
        expected = 4
        assert actual == expected
        
        
class TestClassifyAngleCrossSection():
    def test_235MPa_class_three(self):
        actual = csc.classify_angle_cross_section(mm(130), mm(50), mm(10), MPa(235))
        expected = 3
        assert actual == expected
        
    def test_335MPa_class_four(self):
        actual = csc.classify_angle_cross_section(mm(130), mm(50), mm(10), MPa(355))
        expected = 4
        assert actual == expected