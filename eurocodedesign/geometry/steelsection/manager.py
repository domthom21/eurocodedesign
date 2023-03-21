""" 
module for loading and managing the steel section database
"""

import os
import pandas as pd

from pathlib import Path
from eurocodedesign.geometry.steelsection.steelsections import (
    SteelSection,
    RolledISection,
    CircHollowSection,
    RectHollowSection,
    SquareHollowSection,
)

SECTION_DATA = {
    "HEA": {"filename": "hea_en10365_2017.csv", "section_class": RolledISection},
    "HEB": {"filename": "heb_en10365_2017.csv", "section_class": RolledISection},
    "HEM": {"filename": "hem_en10365_2017.csv", "section_class": RolledISection},
    "IPE": {"filename": "ipe_en10365_2017.csv", "section_class": RolledISection},
    "UB": {"filename": "ub_en10365_2017.csv", "section_class": RolledISection},
    "UC": {"filename": "uc_en10365_2017.csv", "section_class": RolledISection},
    "CHS": {
        "filename": "chs_en10219_en10210_2006.csv",
        "section_class": CircHollowSection,
    },
    "SHS": {
        "filename": "shs_en10219_en10210_2006.csv",
        "section_class": SquareHollowSection,
    },
    "RHS": {
        "filename": "rhs_en10219_en10210_2006.csv",
        "section_class": RectHollowSection,
    },
}


def get_data_path() -> Path:
    """returns the path to where the csv data files are stored"""
    return Path(os.path.dirname(os.path.realpath(__file__))) / "_data"


def is_valid_type(section_name: str) -> bool:
    """checks that the section type provided is valid

    A section type is valid if a csv datafile exists for the section type
    provided by section_name, e.g. "IPE", "HEA", "CHS", etc.

    Args:
        section_name (str): name of the section section e.g. "IPE100"
    Returns:
        bool: True if the section type is valid, False otherwise
    """
    for section_type in SECTION_DATA.keys():
        if section_type in section_name:
            filepath = get_data_path() / SECTION_DATA[section_type]["filename"]
            return os.path.exists(filepath)
        else:
            pass
    return False


def import_section_database(section_type: str) -> pd.DataFrame:
    """imports the data for the chosen section type as a pandas dataframe

    Assumes that the section type exists in the SECTION_DATA constant

    Args:
        section_type (str): type of section e.g. "IPE", "CHS", "UB", etc.

    Returns:
        pd.DataFrame: containing all the geometric data for the profiles for the
            provided section_type
    """
    filepath = get_data_path() / SECTION_DATA[section_type]["filename"]
    return pd.read_csv(filepath, index_col=0)


def is_valid_section(section: str, section_df: pd.DataFrame) -> bool:
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


def get_section_type(section_name: str) -> str | None:
    """gets the section_type from the provide section name

    The section type is assumed to be given by all the letters in section_name
    until the occurence of the first digit.

    Args:
        section_name (str): the name of the steel section e.g. "IPE100", "CHS63x2.3"

    Returns:
        str|None: the first letters of the name. None if there are no digits in
            section_name
    """
    temp = 0
    for chr in section_name:
        # checking if character is numeric,
        # saving index
        if chr.isdigit():
            temp = section_name.index(chr)
            return section_name[0:temp]
    return None


def load_section_props(section_name: str) -> pd.Series:
    """retrieves the section properties for the given section

    Args:
        section_name (str): the name of the steel section e.g. "IPE100", "CHS63x2.3"

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
        if is_valid_type(section_name):
            section_type = get_section_type(section_name)
            section_db = import_section_database(section_type)
            if is_valid_section(section_name, section_db):
                return section_db.loc[section_name]
            else:
                raise ValueError(f"Invalid section name: '{section_name}'")
        else:
            raise ValueError(f"Invalid section type for section: '{section_name}'")


def get_section(section_name: str) -> SteelSection:
    """gets the geometric properties of the section
    
    creates and SteelSection object with the appropriate geometric properties for
    the section with the name section_name

    Args:
        section_name (str): the name of the steel section e.g. "IPE100", "CHS63x2.3"

    Returns:
        SteelSection: object containing the geometric properties of the section
    """
    section_props = load_section_props(section_name)
    section_type = get_section_type(section_name)
    section_class = SECTION_DATA[section_type]["section_class"]
    return section_class(section_name, *section_props.tolist())


if __name__ == "__main__":
    a = "IPE240"
    prof = get_section(a)
    print(prof)
