"""
STEEL PROFILE CLASSES
"""
import os
from typing import Any

from dataclasses import dataclass
import pandas as pd
from pathlib import Path

from eurocodedesign.geometry.section import BasicSection


@dataclass(frozen=True)
class SteelSection(BasicSection):
    # add functionality if required later
    # ??? possible functionality could include calculation of axial, shear, and
    # ??? bending moment strengths -- with a steel material class as input
    pass


@dataclass(frozen=True)
class RolledSection(SteelSection):
    pass


@dataclass(frozen=True)
class WeldedSection(SteelSection):
    pass


@dataclass(frozen=True)
class ISection(SteelSection):
    pass


@dataclass(frozen=True)
class HollowSection(SteelSection):
    pass


@dataclass(frozen=True)
class RolledISection(RolledSection, ISection):
    height: float
    flange_width: float
    web_thickness: float
    flange_thickness: float
    root_radius: float
    weight: float
    perimeter: float
    area: float
    shear_area_z: float
    shear_area_y: float
    second_moment_of_area_y: float
    radius_of_gyration_y: float
    elastic_section_modulus_y: float
    plastic_section_modulus_y: float
    second_moment_of_area_z: float
    radius_of_gyration_z: float
    elastic_section_modulus_z: float
    plastic_section_modulus_z: float
    torsion_constant: float
    torsion_modulus: float
    warping_constant: float
    warping_modulus: float


@dataclass(frozen=True)
class CircularHollowSection(HollowSection):
    diameter: float
    wall_thickness: float
    weight: float
    perimeter: float
    area: float
    shear_area: float
    second_moment_of_area: float
    radius_of_gyration: float
    elastic_section_modulus: float
    plastic_section_modulus: float
    torsion_constant: float
    torsion_modulus: float
    manufacture_method: str


@dataclass(frozen=True)
class RectangularHollowSection(HollowSection):
    height: float
    width: float
    wall_thickness: float
    outer_corner_radius: float
    inner_corner_radius: float
    weight: float
    perimeter: float
    area: float
    shear_area_z: float
    shear_area_y: float
    second_moment_of_area_y: float
    radius_of_gyration_y: float
    elastic_section_modulus_y: float
    plastic_section_modulus_y: float
    second_moment_of_area_z: float
    radius_of_gyration_z: float
    elastic_section_modulus_z: float
    plastic_section_modulus_z: float
    torsion_constant: float
    torsion_modulus: float
    manufacture_method: str


@dataclass(frozen=True)
class SquareHollowSection(HollowSection):
    width: float
    wall_thickness: float
    outer_corner_radius: float
    inner_corner_radius: float
    weight: float
    perimeter: float
    area: float
    shear_area: float
    second_moment_of_area: float
    radius_of_gyration: float
    elastic_section_modulus: float
    plastic_section_modulus: float
    torsion_constant: float
    torsion_modulus: float
    manufacture_method: str


"""
MODULE LEVEL CONSTANTS
"""

_SECTION_DATA = {
    "HEA": {"filename": "hea_en10365_2017.csv",
            "section_class": RolledISection},
    "HEB": {"filename": "heb_en10365_2017.csv",
            "section_class": RolledISection},
    "HEM": {"filename": "hem_en10365_2017.csv",
            "section_class": RolledISection},
    "IPE": {"filename": "ipe_en10365_2017.csv",
            "section_class": RolledISection},
    "UB": {"filename": "ub_en10365_2017.csv",
           "section_class": RolledISection},
    "UC": {"filename": "uc_en10365_2017.csv",
           "section_class": RolledISection},
    "CHS": {
        "filename": "chs_en10219_en10210_2006.csv",
        "section_class": CircularHollowSection,
    },
    "SHS": {
        "filename": "shs_en10219_en10210_2006.csv",
        "section_class": SquareHollowSection,
    },
    "RHS": {
        "filename": "rhs_en10219_en10210_2006.csv",
        "section_class": RectangularHollowSection,
    },
}


"""
MODULE LEVEL DEFINITIONS
"""


def _get_data_path() -> Path:
    """returns the path to where the csv data files are stored"""
    return Path(os.path.dirname(os.path.realpath(__file__))) / "_data"


def _is_valid_type(section_name: str) -> bool:
    """checks that the section type provided is valid

    A section type is valid if a csv datafile exists for the section type
    provided by section_name, e.g. "IPE", "HEA", "CHS", etc.

    Args:
        section_name (str): name of the section section e.g. "IPE100"
    Returns:
        bool: True if the section type is valid, False otherwise
    """
    for section_type in _SECTION_DATA.keys():
        if section_type in section_name:
            filepath = _get_data_path() \
                       / str(_SECTION_DATA[section_type]["filename"])
            return os.path.exists(filepath)
    return False


def _import_section_database(section_type: str) -> pd.DataFrame:
    """imports the data for the chosen section type as a pandas dataframe

    Assumes that the section type exists in the _SECTION_DATA constant

    Args:
        section_type (str): type of section e.g. "IPE", "CHS", "UB", etc.

    Returns:
        pd.DataFrame: containing all the geometric data for
        the profiles for the provided section_type
    """

    filepath = _get_data_path() / _SECTION_DATA[section_type]["filename"]
    df = pd.read_csv(filepath, index_col=0)
    df = df.iloc[1:]
    cols = df.columns.difference(['manufacture'])
    df[cols] = df[cols].astype(float)
    return df


def _is_valid_section(section: str, section_df: pd.DataFrame) -> bool:
    """checks if the section is a valid choice

    checks that section is a valid index in section_df

    Args:
        section (str): the name of the steel section e.g. "IPE100", "CHS63x2.3"
        section_df (pd.DataFrame): dataframe containing all the geometric data
            for the profiles for the provided section type

    Returns:
        bool: True is section is a valid index, False otherwise
    """
    return section in section_df.index


def _get_section_type(section_name: str) -> str | None:
    """gets the section_type from the provide section name

    The section type is assumed to be given by all the letters in section_name
    until the occurence of the first digit.

    Args:
        section_name (str): the name of the steel section
                            e.g. "IPE100", "CHS63x2.3"

    Returns:
        str|None: the first letters of the name. None if there are no digits in
            section_name
    """
    temp = 0
    for chr in section_name:
        if chr.isdigit():
            temp = section_name.index(chr)
            return section_name[0:temp]
    return None


def _load_section_props(section_name: str) -> Any:
    """retrieves the section properties for the given section

    Args:
        section_name (str): the name of the steel section
                            e.g. "IPE100", "CHS63x2.3"

    Raises:
        ValueError: occurs when input is not a string
        ValueError: occurs when the section_name is not in the database
        ValueError: occurs when there is not database for section_type

    Returns:
        pd.Series: containing all the geometric data for the profile
    """
    if type(section_name) != str:
        raise ValueError("Provide the section name as a string e.g. 'IPE100'")
    else:
        if not _is_valid_type(section_name):
            raise ValueError(f"Invalid section type for section: "
                             f"'{section_name}'")
        section_type = _get_section_type(section_name)
        if not section_type:
            raise ValueError
        section_db = _import_section_database(section_type)
        if _is_valid_section(section_name, section_db):
            return section_db.loc[section_name]
        raise ValueError(f"Invalid section name: '{section_name}'")


def _get_section(section_name: str) -> SteelSection:
    """gets the geometric properties of the section

    creates and SteelSection object with the appropriate geometric
     properties for the section with the name section_name

    Args:
        section_name (str): the name of the steel section
                            e.g. "IPE100", "CHS63x2.3"

    Returns:
        SteelSection: object containing the geometric properties of the section
    """
    section_props = _load_section_props(section_name)
    section_type = _get_section_type(section_name)
    if not section_type:
        raise ValueError
    section_class = _SECTION_DATA[section_type]["section_class"]
    if not isinstance(section_class, type(SteelSection)):
        raise TypeError
    return section_class(section_name, *section_props.tolist())


def get(section_name: str) -> SteelSection:
    return _get_section(section_name)
