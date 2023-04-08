"""
tests for the module responsible for loading steel section geometry
eurocodedesign.geometry.steelsection.manager
"""

import pytest
import pandas as pd
import eurocodedesign.geometry.steelsections as ss
from unittest.mock import patch


@pytest.fixture
def section_dataframe():
    # set up test section database for the
    index = ["IPE100", "IPE240", "IPE270", "IPE400"]
    columns = ["A", "I", "Wel", "Wpl"]
    data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    return pd.DataFrame(data, columns=columns, index=index)


@pytest.fixture
def profile_series():
    index = ["A", "I", "Wel", "Wpl"]
    name = "IPE270"
    data = [9, 10, 11, 12]
    return pd.Series(data, index=index, name=name)


@pytest.fixture
def dummy_IPE270():
    geometric_properties = [
        "IPE270",
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
    return ss.RolledISection(*geometric_properties)


@pytest.fixture
def IPE_dataframe():
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
    with pytest.raises(ValueError):
        ss._load_section_props(2)


def test_load_section_props_input_is_wrong_type():
    with pytest.raises(
        ValueError, match="Invalid section type for section: 'XYZ281'"
    ):
        ss._load_section_props("XYZ281")


def test_load_section_props_input_is_wrong_section():
    with pytest.raises(
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
def test_get_section(section_data, IPE_dataframe, dummy_IPE270):
    section_data.return_value = IPE_dataframe
    assert ss._get_section("IPE270") == dummy_IPE270
