"""
tests for the module responsible for loading steel section geometry
eurocodedesign.geometry.steelsection.manager
"""

from pytest import fixture, raises
import pandas as pd
import eurocodedesign.geometry.steelsections as ss
from unittest.mock import patch


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
        "height": 270,
        "flange_width": 135,
        "web_thickness": 6.6,
        "flange_thickness": 10.2,
        "root_radius": 15,
        "weight": 36.1,
        "perimeter": 1.041,
        "area": 4595,
        "shear_area_z": 2214,
        "shear_area_y": 2754,
        "second_moment_of_area_y": 57900000,
        "radius_of_gyration_y": 112.3,
        "elastic_section_modulus_y": 428900,
        "plastic_section_modulus_y": 484000,
        "second_moment_of_area_z": 4199000,
        "radius_of_gyration_z": 30.2,
        "elastic_section_modulus_z": 62200,
        "plastic_section_modulus_z": 96950,
        "torsion_constant": 157100,
        "torsion_modulus": 23800,
        "warping_constant": 69469000000,
        "warping_modulus": 7974000,
    }
    return ss.RolledISection(**geometric_properties)

@fixture
def dummy_IPE240():
    geometric_properties = {
        "name": "IPE240",
        "height": 240,
        "flange_width": 120,
        "web_thickness": 6.2,
        "flange_thickness": 9.8,
        "root_radius": 15,
        "weight": 30.7,
        "perimeter": 0.922,
        "area": 3912,
        "shear_area_z": 1914,
        "shear_area_y": 2352,
        "second_moment_of_area_y": 38920000,
        "radius_of_gyration_y": 99.7,
        "elastic_section_modulus_y": 324300,
        "plastic_section_modulus_y": 366600,
        "second_moment_of_area_z": 2836000,
        "radius_of_gyration_z": 26.9,
        "elastic_section_modulus_z": 47270,
        "plastic_section_modulus_z": 73920,
        "torsion_constant": 127400,
        "torsion_modulus": 20550,
        "warping_constant": 36680000000,
        "warping_modulus": 5354000,
    }
    return ss.RolledISection(**geometric_properties)

@fixture
def dummy_CHS114x3():
    geometric_properties = {
        "name": "CSH114.3x3",
        "weight": 8.23,
        "perimeter": 359,
        "area": 1049,
        "shear_area_z": 668,
        "second_moment_of_area_y": 1625000,
        "radius_of_gyration_y": 39.4,
        "elastic_section_modulus_y": 28440,
        "plastic_section_modulus_y": 37170,
        "diameter": 114.3,
        "wall_thickness": 3,
        "torsion_constant": 3251000,
        "torsion_modulus": 56880,
        "manufacture_method": "cold",
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
        "tw",
        "tf",
        "r",
        "m",
        "P",
        "A",
        "Avz",
        "Avy",
        "Iy",
        "iy",
        "Wely",
        "Wply",
        "Iz",
        "iz",
        "Welz",
        "Wplz",
        "IT",
        "WT",
        "Iw",
        "Ww",
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


@patch("eurocodedesign.geometry.steelsections._import_section_database")
def test_load_section_props_for_valid_section_name(
    imported_df, section_dataframe, profile_series
):
    imported_df.return_value = section_dataframe
    actual = ss._load_section_props("IPE270")
    expected = profile_series
    assert all(actual == expected) is True


@patch("eurocodedesign.geometry.steelsections._import_section_database")
def test_get_section(section_data, ipe_dataframe, dummy_IPE270):
    section_data.return_value = ipe_dataframe
    assert ss._get_section("IPE270") == dummy_IPE270
    

class TestGetOptimal:
    def test_invalid_section_type(self, ipe_dataframe):
        with raises(ValueError, match=r"Invalid section type: 'IPF'"):
            ss.get_optimal("IPF", "area", 4400, "min")
    
    def test_invalid_property(self):
        with raises(ValueError, match=r"Invalid property: 'areb'"):
            ss.get_optimal("IPE", "areb", 4400, "min")
    
    def test_invalid_minmax(self):
        with raises(ValueError, match=r"Invalid min_max value: 'mit'"):
            ss.get_optimal("IPE", "area", 4400, "mit")
            
    def test_ipe_area_min(self, dummy_IPE270):
        actual = ss.get_optimal("IPE", "area", 4400, "min")
        expected = dummy_IPE270
        assert actual == expected

    def test_ipe_area_max(self, dummy_IPE240):
        actual = ss.get_optimal("IPE", "area", 4400, "max")
        expected = dummy_IPE240
        assert actual == expected
        
    def test_ipe_Wpl_min(self, dummy_IPE270):
        actual = ss.get_optimal("IPE", "plastic_section_modulus_y", 428000, "min")
        expected = dummy_IPE270
        assert actual == expected
        
    def test_chs_Wpl_min(self, dummy_CHS114x3):
        actual = ss.get_optimal("CHS", "plastic_section_modulus_y", 37100, "min")
        expected = dummy_CHS114x3
        assert actual == expected
    
        
class TestIsValidPropety:
    def test_invalid_property(self, ipe_dataframe):
        assert ss._is_valid_property(ipe_dataframe, "areb") == False
        
    def test_valid_property(self, ipe_dataframe):
        assert ss._is_valid_property(ipe_dataframe, "area") == True
