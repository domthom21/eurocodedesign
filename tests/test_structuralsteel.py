""" Tests for the constructionsteel module
"""

from pytest import fixture, raises
import eurocodedesign.materials.structuralsteel as ss


@fixture
def S235_thin_material():
    return ss.S235()


@fixture
def S235_thick_material():
    return ss.S235(False)


def test_fy_getter_with_thin_material(S235_thin_material):
    assert S235_thin_material.f_yk == 235


def test_fu_getter_with_thin_material(S235_thin_material):
    assert S235_thin_material.f_uk == 360


def test_fy_getter_with_thick_material(S235_thick_material):
    assert S235_thick_material.f_yk == 215


def test_fu_getter_with_thick_material(S235_thick_material):
    assert S235_thick_material.f_uk == 360


def test_get_for_structural_steel_types_with_steel_in_library_t_less_equal_40(
    S235_thin_material,
):
    assert ss.get("S235") == S235_thin_material


def test_get_for_structural_steel_types_with_steel_in_library_t_greater_40(
    S235_thick_material,
):
    assert ss.get("S235", False) == S235_thick_material


def test_get_for_structural_steel_types_with_steel_not_in_library():
    with raises(ValueError, match="Steel material '211' not in library"):
        ss.get("211", True)


def test_property_E(S235_thick_material):
    assert S235_thick_material.E == 210_000


def test_property_G(S235_thick_material):
    assert S235_thick_material.G == 81_000


def test_property_alpha(S235_thick_material):
    assert S235_thick_material.alpha == 1.2e-7
