""" Tests for the constructionsteel module
"""

from pytest import fixture
from eurocodedesign.material.constructionsteel import S235


@fixture
def S235_thin_material():
    return S235()


@fixture
def S235_thick_material():
    return S235(False)


def test_fy_getter_with_thin_material(S235_thin_material):
    assert S235_thin_material.fy == 235


def test_fu_getter_with_thin_material(S235_thin_material):
    assert S235_thin_material.fu == 360


def test_fy_getter_with_thick_material(S235_thick_material):
    assert S235_thick_material.fy == 215


def test_fu_getter_with_thick_material(S235_thick_material):
    assert S235_thick_material.fu == 360
    
    
