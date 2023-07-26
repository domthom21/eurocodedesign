"""
tests for the module responsible for loading steel section geometry
eurocodedesign.geometry.steelsection.manager
"""

from unittest.mock import patch

import pandas as pd
from pytest import fixture, raises

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
def dummy_CHS114x3():
    geometric_properties = {
        "name": "CSH114.3x3",
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


def test_when_is_valid_type():
    assert ss._is_valid_type("HEM600") is True


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


def test_load_section_props_input_not_string():
    with raises(ValueError):
        ss._load_section_props(2)


def test_load_section_props_input_is_wrong_type():
    with raises(
        ValueError, match="Invalid section type for section: 'XYZ281'"
    ):
        ss._load_section_props("XYZ281")


def test_load_section_props_input_is_wrong_section():
    with raises(
        ValueError, match="Invalid section name: 'IPE281'"
    ):
        ss._load_section_props("IPE281")


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
