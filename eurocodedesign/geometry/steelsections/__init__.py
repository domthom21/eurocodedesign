"""
STEEL PROFILE CLASSES
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Type

import pandas as pd

from eurocodedesign.geometry.section import BasicSection


@dataclass(frozen=True)
class SteelSection(BasicSection):
    # properties common among all steel sections (incl. major axis bending)
    weight: float = field(kw_only=True)
    perimeter: float = field(kw_only=True)
    area: float = field(kw_only=True)
    shear_area_z: float = field(kw_only=True)
    second_moment_of_area_y: float = field(kw_only=True)
    radius_of_gyration_y: float = field(kw_only=True)
    elastic_section_modulus_y: float = field(kw_only=True)
    plastic_section_modulus_y: float = field(kw_only=True)
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
    height: float = field(kw_only=True)
    flange_width: float = field(kw_only=True)
    web_thickness: float = field(kw_only=True)
    flange_thickness: float = field(kw_only=True)
    shear_area_y: float = field(kw_only=True)
    second_moment_of_area_z: float = field(kw_only=True)
    radius_of_gyration_z: float = field(kw_only=True)
    elastic_section_modulus_z: float = field(kw_only=True)
    plastic_section_modulus_z: float = field(kw_only=True)
    torsion_constant: float = field(kw_only=True)
    torsion_modulus: float = field(kw_only=True)
    warping_constant: float = field(kw_only=True)
    warping_modulus: float = field(kw_only=True)


@dataclass(frozen=True)
class HollowSection(SteelSection):
    pass


@dataclass(frozen=True)
class RolledISection(RolledSection, ISection):
    root_radius: float = field(kw_only=True)


@dataclass(frozen=True)
class CircularHollowSection(HollowSection):
    diameter: float = field(kw_only=True)
    wall_thickness: float = field(kw_only=True)
    torsion_constant: float = field(kw_only=True)
    torsion_modulus: float = field(kw_only=True)
    manufacture_method: str = field(kw_only=True)


@dataclass(frozen=True)
class RectangularHollowSection(HollowSection):
    height: float = field(kw_only=True)
    width: float = field(kw_only=True)
    wall_thickness: float = field(kw_only=True)
    outer_corner_radius: float = field(kw_only=True)
    inner_corner_radius: float = field(kw_only=True)
    shear_area_y: float = field(kw_only=True)
    second_moment_of_area_z: float = field(kw_only=True)
    radius_of_gyration_z: float = field(kw_only=True)
    elastic_section_modulus_z: float = field(kw_only=True)
    plastic_section_modulus_z: float = field(kw_only=True)
    torsion_constant: float = field(kw_only=True)
    torsion_modulus: float = field(kw_only=True)
    manufacture_method: str = field(kw_only=True)


@dataclass(frozen=True)
class SquareHollowSection(RectangularHollowSection):
    pass


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

# used to link the variable names in the csv data to variable names in code
_PROPERTY_NAME_MAP: Dict[str, Dict[str, Type[float] | Type[str] | str]] = {
    # TODO change float to abstractunit
    "h": {"variable_name": "height",
          "type": float},
    "b": {"variable_name": "flange_width",
          "type": float},
    "tw": {"variable_name": "web_thickness",
           "type": float},
    "tf": {"variable_name": "flange_thickness",
           "type": float},
    "r": {"variable_name": "root_radius",
          "type": float},
    "m": {"variable_name": "weight",
          "type": float},
    "P": {"variable_name": "perimeter",
          "type": float},
    "A": {"variable_name": "area",
          "type": float},
    "Avz": {"variable_name": "shear_area_z",
            "type": float},
    "Avy": {"variable_name": "shear_area_y",
            "type": float},
    "Iy": {"variable_name": "second_moment_of_area_y",
           "type": float},
    "iy": {"variable_name": "radius_of_gyration_y",
           "type": float},
    "Wely": {"variable_name": "elastic_section_modulus_y",
             "type": float},
    "Wply": {"variable_name": "plastic_section_modulus_y",
             "type": float},
    "Iz": {"variable_name": "second_moment_of_area_z",
           "type": float},
    "iz": {"variable_name": "radius_of_gyration_z",
           "type": float},
    "Welz": {"variable_name": "elastic_section_modulus_z",
             "type": float},
    "Wplz": {"variable_name": "plastic_section_modulus_z",
             "type": float},
    "IT": {"variable_name": "torsion_constant",
           "type": float},
    "WT": {"variable_name": "torsion_modulus",
           "type": float},
    "Iw": {"variable_name": "warping_constant",
           "type": float},
    "Ww": {"variable_name": "warping_modulus",
           "type": float},
    "t": {"variable_name": "wall_thickness",
          "type": float},
    "ro": {"variable_name": "outer_corner_radius",
           "type": float},
    "ri": {"variable_name": "inner_corner_radius",
           "type": float},
    "manufacture": {"variable_name": "manufacture_method",
                    "type": str},
    "Av": {"variable_name": "shear_area_z",
           "type": float},  # for CHS and SHS sections
    "I": {"variable_name": "second_moment_of_area_y",
          "type": float},  # for CHS and SHS sections
    "i": {"variable_name": "radius_of_gyration_y",
          "type": float},  # for CHS and SHS sections
    "Wel": {"variable_name": "elastic_section_modulus_y",
            "type": float},  # for CHS and SHS sections
    "Wpl": {"variable_name": "plastic_section_modulus_y",
            "type": float},  # for CHS and SHS sections
    "D": {"variable_name": "diameter",
          "type": float},  # for CHS and SHS sections
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

    filepath = _get_data_path() / str(_SECTION_DATA[section_type]["filename"])
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
    return section_class(section_name, **_map_property_names(section_props))


def _map_property_names(section_props: Any) -> Dict[str, Any]:
    return {str(_PROPERTY_NAME_MAP[k]["variable_name"]): _PROPERTY_NAME_MAP[k][
        "type"](v) for k, v in
            section_props.items()}  # type: ignore[operator]


def get(section_name: str) -> SteelSection:
    return _get_section(section_name)


def get_optimal(section_type: str, prop: str, val: float,
                min_max: str) -> SteelSection:
    if not _is_valid_type(section_type):
        raise ValueError(f"Invalid section type: '{section_type}'")

    df = _import_section_database(section_type)

    if not _is_valid_property(df, prop):
        raise ValueError(f"Invalid property: '{prop}'")

    if section_type == "CHS":
        prop_key = _property_key_chs(prop)
    else:
        prop_key = _property_key(prop)

    if min_max == "min":
        df_filtered = df[df[prop_key] >= val]
        idx_min = df_filtered[prop_key].idxmin()
        return get(str(idx_min))

    elif min_max == "max":
        df_filtered = df[df[prop_key] <= val]
        idx_max = df_filtered[prop_key].idxmax()
        return get(str(idx_max))

    else:
        raise ValueError(f"Invalid min_max value: '{min_max}'")


def _is_valid_property(df: pd.DataFrame, prop: str) -> bool:
    # map the keys from dataframe to allow comparison
    props = [str(_PROPERTY_NAME_MAP[k]["variable_name"]) for k in df.columns]
    if prop in props:
        return True
    return False


def _property_key_chs(prop: str) -> str:
    temp_map = {v["variable_name"]: k for k, v in _PROPERTY_NAME_MAP.items()}
    return temp_map[prop]


def _property_key(prop: str) -> str:
    bad_keys = ["Av", "I", "i", "Wel", "Wpl"]
    temp_map = {v["variable_name"]: k for k, v in _PROPERTY_NAME_MAP.items()
                if k not in bad_keys}
    return temp_map[prop]
