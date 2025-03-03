"""
tests for the module responsible for loading steel section geometry
eurocodedesign.geometry.steelsection.manager
"""

from unittest.mock import patch

import pandas as pd
from pytest import fixture, raises, approx

import eurocodedesign.geometry.steelsections as ss


@fixture
def section_dataframe():
    # set up test section database for the
    index = ["IPE100", "IPE240", "IPE270", "IPE400"]
    columns = ["A", "I", "Wel", "Wpl"]
    data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    return pd.DataFrame(data, columns=columns, index=index)


@fixture
def profile_series():
    index = ["A", "I", "Wel", "Wpl"]
    name = "IPE270"
    data = [9, 10, 11, 12]
    return pd.Series(data, index=index, name=name)


@fixture
def dummy_IPE270():
    geometric_properties = {
        "name": "IPE270",
        "h": 270,
        "b": 135,
        "t_w": 6.6,
        "t_f": 10.2,
        "r": 15,
        "m": 36.1,
        "P": 1.041,
        "A": 4595,
        "A_vz": 2214,
        "A_vy": 2754,
        "I_y": 57900000,
        "i_y": 112.3,
        "W_ely": 428900,
        "W_ply": 484000,
        "I_z": 4199000,
        "i_z": 30.2,
        "W_elz": 62200,
        "W_plz": 96950,
        "I_T": 157100,
        "W_T": 23800,
        "I_w": 69469000000,
        "W_w": 7974000,
    }
    return ss.RolledISection(**geometric_properties)


@fixture
def dummy_IPE240():
    geometric_properties = {
        "name": "IPE240",
        "h": 240,
        "b": 120,
        "t_w": 6.2,
        "t_f": 9.8,
        "r": 15,
        "m": 30.7,
        "P": 0.922,
        "A": 3912,
        "A_vz": 1914,
        "A_vy": 2352,
        "I_y": 38920000,
        "i_y": 99.7,
        "W_ely": 324300,
        "W_ply": 366600,
        "I_z": 2836000,
        "i_z": 26.9,
        "W_elz": 47270,
        "W_plz": 73920,
        "I_T": 127400,
        "W_T": 20550,
        "I_w": 36680000000,
        "W_w": 5354000,
    }
    return ss.RolledISection(**geometric_properties)


@fixture
def dummy_HL1000B():
    geometric_properties = {
        "name": "IPE240",
        "h": 1000,
        "b": 400,
        "t_w": 19.0,
        "t_f": 36.1,
        "r": 30,
        "m": 371.1,
        "P": 3.510,
        "A": 47280,
        "A_vz": 18187,
        "A_vy": 23016,
        "I_y": 8137000000,
        "i_y": 414.9,
        "W_ely": 16270000,
        "W_ply": 18360000,
        "I_z": 385800000,
        "i_z": 90.3,
        "W_elz": 1929000,
        "W_plz": 2984000,
        "I_T": 15750000,
        "W_T": 436290,
        "I_w": 8.944e13,
        "W_w": 927897100,
    }
    return ss.RolledISection(**geometric_properties)


@fixture
def dummy_CHS114x3():
    geometric_properties = {
        "name": "CHS114.3x3",
        "m": 8.23,
        "P": 0.359,
        "A": 1049,
        "A_vz": 668,
        "I_y": 1625000,
        "i_y": 39.4,
        "W_ely": 28440,
        "W_ply": 37170,
        "A_vy": 668,
        "I_z": 1625000,
        "i_z": 39.4,
        "W_elz": 28440,
        "W_plz": 37170,
        "D": 114.3,
        "t": 3,
        "I_T": 3251000,
        "W_T": 56880,
        "manufacture": "cold",
    }
    return ss.CircularHollowSection(**geometric_properties)


@fixture
def dummy_L100x10():
    geometric_properties = {
        "name": "L100x10",
        "h": 100,
        "b": 100,
        "t": 10,
        "A": 1920,
        "m": 15,
        "r_1": 12,
        "r_2": 6,
        "c_y": 28.2,
        "c_z": 28.2,
        "I_y": 1770000,
        "I_z": 1770000,
        "I_u": 2800000,
        "I_v": 730000,
        "i_y": 30.4,
        "i_z": 30.4,
        "i_u": 38.3,
        "i_v": 19.5,
        "W_ely": 24600,
        "W_elz": 24600,
        "I_T": 69700,
        "tan_alpha": 1.0,
    }
    return ss.LSection(**geometric_properties)


@fixture
def ipe_dataframe():
    # set up test section database for the
    geometric_properties_IPE270 = [
        270,
        135,
        6.6,
        10.2,
        15,
        36.1,
        1.041,
        4595,
        2214,
        2754,
        57900000,
        112.3,
        428900,
        484000,
        4199000,
        30.2,
        62200,
        96950,
        157100,
        23800,
        69469000000,
        7974000,
    ]
    geometric_properties_IPE100 = [
        100,
        55,
        4.1,
        5.7,
        7,
        8.1,
        0.4,
        1032,
        508,
        627,
        1710000,
        40.7,
        34200,
        39410,
        159200,
        12.4,
        5789,
        9146,
        11530,
        2812,
        342100000,
        266800,
    ]
    columns = [
        "h",
        "b",
        "t_w",
        "t_f",
        "r",
        "m",
        "P",
        "A",
        "A_vz",
        "A_vy",
        "I_y",
        "i_y",
        "W_ely",
        "W_ply",
        "I_z",
        "i_z",
        "W_elz",
        "W_plz",
        "I_T",
        "W_T",
        "I_w",
        "W_w",
    ]
    data = [geometric_properties_IPE100, geometric_properties_IPE270]
    return pd.DataFrame(data, columns=columns, index=["IPE100", "IPE270"])


@fixture
def dummy_100x60():
    props = {
            "A"	      :     6000,
            "m"	      :     47.1,
            "P"	      :     320,
            "A_vz"    :	    6000,
            "A_vy"    :	    6000,
            "I_y"	  :     5000000,
            "i_y"	  :     28.86751346,
            "W_ely"   :	    100000,
            "W_ply"   :	    150000,
            "I_z"	  :     1800000,
            "i_z"     :	    17.32050808,
            "W_elz"   :	    60000,
            "W_plz"   :	    90000,
            "I_T"     :	    4471200.004,
            "W_T"     :	    84960.00036}
    return props



def test_when_is_valid_type():
    assert ss._is_valid_type("HEM") is True


def test_when_not_is_valid_type_with_empty_string():
    assert ss._is_valid_type("") is False


def test_when_not_is_valid_type_with_invalid_name():
    assert ss._is_valid_type("XRX120") is False


def test_when_is_valid_section(section_dataframe):
    assert ss._is_valid_section("IPE240", section_dataframe) is True


def test_when_not_is_valid_section(section_dataframe):
    assert ss._is_valid_section("IPE617", section_dataframe) is False


def test_when_get_section_type_is_found():
    assert ss._get_section_type("IPE100") == "IPE"


def test_when_get_section_type_is_not_found():
    assert ss._get_section_type("320LRB") == ""


def test_get_section_input_is_wrong_type():
    with raises(
        ValueError, match="Invalid section type for section: 'XYZ281'"
    ):
        ss._get_section("XYZ281")


def test_load_section_props_input_is_wrong_section():
    with raises(
        ValueError, match="Invalid section name: 'IPE281'"
    ):
        ss._load_section_props("IPE281")


def test_load_Lsection(dummy_L100x10):
    actual = ss.get("L100x10")
    assert actual == dummy_L100x10


def test_load_HLsection(dummy_HL1000B):
    actual = ss.get("HL1000B")
    assert actual == dummy_HL1000B


@patch("eurocodedesign.geometry.steelsections.import_section_database")
def test_load_section_props_for_valid_section_name(
    imported_df, section_dataframe, profile_series
):
    imported_df.return_value = section_dataframe
    actual = ss._load_section_props("IPE270")
    expected = profile_series
    assert all(actual == expected) is True


@patch("eurocodedesign.geometry.steelsections.import_section_database")
def test_get_section(section_data, ipe_dataframe, dummy_IPE270):
    section_data.return_value = ipe_dataframe
    assert ss._get_section("IPE270") == dummy_IPE270


class TestGetOptimal:
    def test_invalid_section_type(self, ipe_dataframe):
        with raises(ValueError, match=r"Invalid section type: 'IPF'"):
            ss.get_optimal("IPF", "A", 4400, "min")

    def test_invalid_property(self):
        with raises(ValueError, match=r"Invalid property: 'areb'"):
            ss.get_optimal("IPE", "areb", 4400, "min")

    def test_invalid_minmax(self):
        with raises(ValueError, match=r"Invalid min_max value: 'mit'"):
            ss.get_optimal("IPE", "A", 4400, "mit")

    def test_ipe_area_min(self, dummy_IPE270):
        actual = ss.get_optimal("IPE", "A", 4400, "min")
        expected = dummy_IPE270
        assert actual == expected

    def test_ipe_area_max(self, dummy_IPE240):
        actual = ss.get_optimal("IPE", "A", 4400, "max")
        expected = dummy_IPE240
        assert actual == expected

    def test_ipe_Wpl_min(self, dummy_IPE270):
        actual = ss.get_optimal("IPE", "W_ply", 428000,
                                "min")
        expected = dummy_IPE270
        assert actual == expected

    def test_chs_Wpl_min(self, dummy_CHS114x3):
        actual = ss.get_optimal("CHS", "W_ply", 37100,
                                "min")
        expected = dummy_CHS114x3
        assert actual == expected


class TestIsValidPropety:
    def test_invalid_property(self, ipe_dataframe):
        assert ss._is_valid_property(ipe_dataframe, "areb") is False

    def test_valid_property(self, ipe_dataframe):
        assert ss._is_valid_property(ipe_dataframe, "A") is True


class TestTorsionFactors:
    def test_shape(self):
        assert ss.rect_section_torsion_factors().shape == (9,3)

    def test_value(self):
        assert ss.rect_section_torsion_factors()[2, 1] == 0.196


class TestRectangularSolidSection:
    def test_alpha(self):
        section = ss.RectangularSolidSection(100, 60)
        assert section._alpha() == approx(0.2070000022)

    def test_beta(self):
        section = ss.RectangularSolidSection(100, 60)
        assert section._beta() == approx(0.236000001)

    def test_properties(self, dummy_100x60):
        section = ss.RectangularSolidSection(100, 60)
        assert all([section.A == approx(dummy_100x60["A"]),
                   section.m == approx(dummy_100x60["m"]),
                   section.P == approx(dummy_100x60["P"]),
                   section.A_vz == approx(dummy_100x60["A_vz"]),
                   section.A_vy == approx(dummy_100x60["A_vy"]),
                   section.I_y == approx(dummy_100x60["I_y"]),
                   section.i_y == approx(dummy_100x60["i_y"]),
                   section.W_ely == approx(dummy_100x60["W_ely"]),
                   section.W_ply == approx(dummy_100x60["W_ply"]),
                   section.I_z == approx(dummy_100x60["I_z"]),
                   section.i_z == approx(dummy_100x60["i_z"]),
                   section.W_elz == approx(dummy_100x60["W_elz"]),
                   section.W_plz == approx(dummy_100x60["W_plz"]),
                   section.I_T == approx(dummy_100x60["I_T"]),
                   section.W_T == approx(dummy_100x60["W_T"])])
        
    def test_get(self):
        section = ss.RectangularSolidSection(100, 60)
        assert ss.get("Rect100x60") == section
        

class TestHasValidRectDimensions():
    def test_with_floats(self):
        section_name = "Rect100.3x61.2"
        assert ss._has_valid_rect_dimensions(section_name) is True

    def test_with_ints(self):
        section_name = "Rect100x61"
        assert ss._has_valid_rect_dimensions(section_name) is True

    def test_floats_and_ints(self):
        section_name = "Rect100x61.2"
        assert ss._has_valid_rect_dimensions(section_name) is True

    def test_no_x(self):
        section_name = "Rect40y10"
        ss._has_valid_rect_dimensions(section_name) is False


def test_rect_height_and_width():
    section_name = "Rect100.3x10"
    height, width = ss._rect_height_and_width(section_name)
    assert ((height == 100.3) and (width == 10)) is True
