""" 
module for loading and managing the steel section database
"""

# TODO: add doc strings

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
    # returns the path to the folder where the data csvs are stored
    return Path(os.path.dirname(os.path.realpath(__file__))) / "_data"


def select_section_class(section_name):
    # returns the class of the section
    section_type = get_section_type(section_name)
    if SECTION_DATA[section_type]["section_type"] == "RolledISection":
        return RolledISection


def is_valid_type(section_name: str) -> bool:
    # returns true if the database csv exists for the chosen profile type exists
    for section_type in SECTION_DATA.keys():
        if section_type in section_name:
            filepath = get_data_path() / SECTION_DATA[section_type]["filename"]
            return os.path.exists(filepath)
        else:
            pass
    return False


def import_section_database(section_type: str) -> pd.DataFrame:
    # returns the csv as a pandas dataframe
    # assumes the csv for the chosen section type is available
    filepath = get_data_path() / SECTION_DATA[section_type]["filename"]
    return pd.read_csv(filepath, index_col=0)


def is_valid_section(section: str, section_df: pd.DataFrame) -> bool:
    # returns true if the chosen section is in  the database
    return section in section_df.index


def get_section_props(section: str, section_df: pd.DataFrame) -> pd.Series:
    # extract the section properties of the chosen section from the section dataframe
    # assumes that the chosen section is in the csv
    return section_df.loc[section]


def get_section_type(section: str) -> str | None:
    # extracts the type of section from name of the section
    for section_type in SECTION_DATA.keys():
        if section_type in section:
            return section_type
    return None


def load_section_props(section_name: str) -> pd.Series:
    # returns the section properites of the chosen section
    if type(section_name) != str:
        raise ValueError("Provide the section name as a string e.g. 'IPE100'")
    else:
        if is_valid_type(section_name):
            section_type = get_section_type(section_name)
            if section_type is None:
                # todo: raise error flagging that section is not in database
                pass
            section_db = import_section_database(section_type)
            if is_valid_section(section_name, section_db):
                return get_section_props(section_name, section_db)


def get_section(section_name: str) -> SteelSection:
    # returns a SteelSection object containing the section properties
    section_props = load_section_props(section_name)
    section_type = get_section_type(section_name)
    section_class = SECTION_DATA[section_type]["section_class"]
    return section_class(section_name, *section_props.tolist())


if __name__ == "__main__":
    a = "CHS60.3x2.5"
    prof = get_section(a)
    print(prof)
