"""
STEEL PROFILE CLASSES
"""
import os
import re
from math import sqrt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Type

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike

from eurocodedesign.geometry.section import BasicSection
from eurocodedesign.materials.structuralsteel import DENSITY

@ dataclass(frozen=True)
class SteelSection():
    ...

@dataclass(frozen=True)
class StandardSteelSection(BasicSection):
    # properties common among all steel sections (incl. major axis bending)
    m: float = field(kw_only=True)
    A: float = field(kw_only=True)
    I_y: float = field(kw_only=True)
    i_y: float = field(kw_only=True)
    W_ely: float = field(kw_only=True)
    I_z: float = field(kw_only=True)
    i_z: float = field(kw_only=True)
    W_elz: float = field(kw_only=True)


@dataclass(frozen=True)
class RolledSection(SteelSection):
    pass


@dataclass(frozen=True)
class WeldedSection(SteelSection):
    pass


@dataclass(frozen=True)
class ISection(SteelSection):
    h: float = field(kw_only=True)
    b: float = field(kw_only=True)
    t_w: float = field(kw_only=True)
    t_f: float = field(kw_only=True)
    A_vz: float = field(kw_only=True)
    A_vy: float = field(kw_only=True)
    W_ply: float = field(kw_only=True)
    W_plz: float = field(kw_only=True)
    I_T: float = field(kw_only=True)
    W_T: float = field(kw_only=True)
    I_w: float = field(kw_only=True)
    W_w: float = field(kw_only=True)


@dataclass(frozen=True)
class LSection(RolledSection, StandardSteelSection):
    h: float = field(kw_only=True)
    b: float = field(kw_only=True)
    t: float = field(kw_only=True)
    r_1: float = field(kw_only=True)
    r_2: float = field(kw_only=True)
    c_y: float = field(kw_only=True)
    c_z: float = field(kw_only=True)
    I_u: float = field(kw_only=True)
    I_v: float = field(kw_only=True)
    i_u: float = field(kw_only=True)
    i_v: float = field(kw_only=True)
    I_T: float = field(kw_only=True)
    tan_alpha: float = field(kw_only=True)


@dataclass(frozen=True)
class HollowSection(SteelSection):
    pass


@dataclass(frozen=True)
class RolledISection(RolledSection, ISection, StandardSteelSection):
    r: float = field(kw_only=True)
    P: float = field(kw_only=True)


@dataclass(frozen=True)
class CircularHollowSection(HollowSection, StandardSteelSection):
    D: float = field(kw_only=True)
    P: float = field(kw_only=True)
    t: float = field(kw_only=True)
    A_vz: float = field(kw_only=True)
    A_vy: float = field(kw_only=True)
    W_ply: float = field(kw_only=True)
    W_plz: float = field(kw_only=True)
    I_T: float = field(kw_only=True)
    W_T: float = field(kw_only=True)
    manufacture: str = field(kw_only=True)

    def __post_init__(self) -> None:
        object.__setattr__(self, "A_v", self.A_vz)
        object.__setattr__(self, "I", self.I_y)
        object.__setattr__(self, "i", self.i_y)
        object.__setattr__(self, "W_el", self.W_ely)
        object.__setattr__(self, "W_pl", self.W_ply)
        object.__setattr__(self, "h", self.D)
        object.__setattr__(self, "b", self.D)


@dataclass(frozen=True)
class RectangularHollowSection(HollowSection, StandardSteelSection):
    h: float = field(kw_only=True)
    b: float = field(kw_only=True)
    t: float = field(kw_only=True)
    P: float = field(kw_only=True)
    r_o: float = field(kw_only=True)
    r_i: float = field(kw_only=True)
    A_vz: float = field(kw_only=True)
    A_vy: float = field(kw_only=True)
    W_ply: float = field(kw_only=True)
    W_plz: float = field(kw_only=True)
    I_T: float = field(kw_only=True)
    W_T: float = field(kw_only=True)
    manufacture: str = field(kw_only=True)


@dataclass(frozen=True)
class SquareHollowSection(RectangularHollowSection):
    def __post_init__(self) -> None:
        object.__setattr__(self, "A_v", self.A_vz)
        object.__setattr__(self, "I", self.I_y)
        object.__setattr__(self, "i", self.i_y)
        object.__setattr__(self, "W_el", self.W_ely)
        object.__setattr__(self, "W_pl", self.W_ply)


@dataclass(frozen=True)
class RectangularSolidSection(SteelSection):
    h: float
    b: float

    def __post_init__(self):
        object.__setattr__(self, "name", f"Rect{self.h}x{self.b}")
        object.__setattr__(self, "A", self.h * self.b)
        object.__setattr__(self, "m", self.A * DENSITY / 1e6)
        object.__setattr__(self, "P", 2 * (self.h + self.b))
        object.__setattr__(self, "A_vz", self.A * self.h)
        object.__setattr__(self, "A_vy", self.A * self.b)
        object.__setattr__(self, "I_y", self.b * self.h ** 3 / 12)
        object.__setattr__(self, "i_y", sqrt(self.I_y / self.A))
        object.__setattr__(self, "W_ely", self.b * self.h ** 2 / 6)
        object.__setattr__(self, "W_ply", self.b * self.h ** 2 / 4)
        object.__setattr__(self, "I_z", self.h * self.b ** 3 / 12)
        object.__setattr__(self, "i_z", sqrt(self.I_z / self.A))
        object.__setattr__(self, "W_elz", self.h * self.b ** 2 / 6)
        object.__setattr__(self, "W_plz", self.h * self.b ** 2 / 4)
        object.__setattr__(self, "I_T", self._alpha() * self.h * self. b ** 3)
        object.__setattr__(self, "W_T", self._beta() * self.h * self. b ** 2)

    def _alpha(self):
        data = rect_section_torsion_factors()
        return np.interp(self.h / self.b, data[:,0], data[:,1])

    def _beta(self):
        data = rect_section_torsion_factors()
        return np.interp(self.h / self.b, data[:,0], data[:,2])


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
    "HD": {"filename": "hd_en10365_2017.csv",
           "section_class": RolledISection},
    "HL": {"filename": "hl_en10365_2017.csv",
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
    "L": {"filename": "L_en10056_2017.csv",
          "section_class": LSection
    },
    "Rect": {"filename": "",
             "section_class": RectangularSolidSection}   
}

_NO_FILES = ["Rect"]

# used to link the variable names in the csv data to variable names in code
_PROPERTY_TYPE_MAP: Dict[str, Type[float] | Type[str]] = {
    # TODO change float to abstractunit
    "h": float,
    "b": float,
    "t_w": float,
    "t_f": float,
    "r": float,
    "m": float,
    "P": float,
    "A": float,
    "A_vz": float,
    "A_vy": float,
    "I_y": float,
    "i_y": float,
    "W_ely": float,
    "W_ply": float,
    "I_z": float,
    "i_z": float,
    "W_elz": float,
    "W_plz": float,
    "I_T": float,
    "W_T": float,
    "I_w": float,
    "W_w": float,
    "t": float,
    "r_o": float,
    "r_i": float,
    "manufacture": str,
    "A_v": float,  # for CHS
    "I": float,  # for CHS
    "i": float,  # for CHS
    "W_el": float,  # for CHS
    "W_pl": float,  # for CHS
    "D": float,  # for CHS
    "r_1": float,  # for LSection
    "r_2": float,  # for LSection
    "c_y": float,  # for LSection
    "c_z": float,  # for LSection
    "I_u": float,  # for LSection
    "I_v": float,  # for LSection
    "i_u": float,  # for LSection
    "i_v": float,  # for LSection
    "I_T": float,  # for LSection
    "tan_alpha": float,  # for LSection
}

"""
MODULE LEVEL DEFINITIONS
"""


def _get_data_path() -> Path:
    """returns the path to where the csv data files are stored"""
    return Path(os.path.dirname(os.path.realpath(__file__))) / "_data"


def _is_valid_type(section_type: str) -> bool:
    """checks that the section type provided is valid

    A section type is valid if a csv datafile exists for the section type
    provided by section_name, e.g. "IPE", "HEA", "CHS", etc.

    Args:
        section_type (str): type of section e.g. "IPE", "Rect"
    Returns:
        bool: True if the section type is valid, False otherwise
    """
    if section_type in _SECTION_DATA.keys():
        return True
    return False


def _is_file_available(section_type: str):
    filepath = _get_data_path() / str(_SECTION_DATA[section_type]["filename"])
    return os.path.exists(filepath)


def import_section_database(section_type: str) -> pd.DataFrame:
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
    
    assumes the section_name belongs to valid type of cross-section

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
    # if not isinstance(section_name, str):
    #     raise ValueError("Provide the section name as a string e.g. 'IPE100'")
    # else:
    # if not _is_valid_type(section_name):
    #     raise ValueError(f"Invalid section type for section: "
    #                      f"'{section_name}'")
    section_type = _get_section_type(section_name)
    # if not section_type:
    #     raise ValueError
    section_db = import_section_database(section_type)
    
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

    section_type = _get_section_type(section_name)
    if not _is_valid_type(section_type):
        raise ValueError(f"Invalid section type for section: '{section_name}'")
    
    if not section_type in _NO_FILES:
        if not _is_file_available(section_type):
            raise ValueError(f"No data available for: {section_type}")
        
        section_props = _load_section_props(section_name)
        
        if not section_type:
            raise ValueError
        
        section_class = _SECTION_DATA[section_type]["section_class"]
        if not isinstance(section_class, type(SteelSection)):
            raise TypeError
        return section_class(section_name, **_map_property_names(section_props))
    
    section_class = _SECTION_DATA[section_type]["section_class"]

    if section_type == "Rect":
        height, width = _rect_height_and_width(section_name)
        return section_class(height, width)
        

def _map_property_names(section_props: Any) -> Dict[str, Any]:
    return {str(k): _PROPERTY_TYPE_MAP[k](v) for k, v in section_props.items()}


def get(section_name: str) -> SteelSection:
    return _get_section(section_name)


def get_optimal(section_type: str, prop: str, val: float,
                min_max: str) -> SteelSection:
    if not _is_valid_type(section_type):
        raise ValueError(f"Invalid section type: '{section_type}'")

    df = import_section_database(section_type)

    if not _is_valid_property(df, prop):
        raise ValueError(f"Invalid property: '{prop}'")

    if min_max == "min":
        df_filtered = df[df[prop] >= val]
        idx_min = df_filtered[prop].idxmin()
        return get(str(idx_min))

    elif min_max == "max":
        df_filtered = df[df[prop] <= val]
        idx_max = df_filtered[prop].idxmax()
        return get(str(idx_max))

    else:
        raise ValueError(f"Invalid min_max value: '{min_max}'")


def _is_valid_property(df: pd.DataFrame, prop: str) -> bool:
    # map the keys from dataframe to allow comparison
    if prop in df.columns:
        return True
    return False


def rect_section_torsion_factors() -> ArrayLike:
    file_name = "torsion_factors_rectangular_solid_sections.csv"
    folder = _get_data_path()

    factors = np.loadtxt(folder / file_name, delimiter=",", skiprows=1)
    return factors


def _rect_height_and_width(section_name: str):
    if _has_valid_rect_dimensions(section_name):
        height, width = section_name[4:].split("x")
    return float(height), float(width)


def _has_valid_rect_dimensions(section_name:str):
    """returns true if section_name contains [float]x[float]
    """
    match = re.search(r"\d*\.?\d*+[x]\d*\.?\d*+", section_name)

    if match == None:
        return False
    return True
