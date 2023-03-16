""" 
tests for the module responsible for loading steel section geometry
eurocodedesign.geometry.steelsection.manager
"""

import pytest
import pandas as pd
import eurocodedesign.geometry.steelsection.manager as mgr

# todo: test_get_data_path()
# todo: test_select_section_class()

def test_when_is_valid_type():
    assert mgr.is_valid_type("HEM600") == True
    
def test_when_not_is_valid_type_with_empty_string():
    assert mgr.is_valid_type("") == False

# ??? How do we make sure all of the implemented section types 
# ??? are tested?    
def test_when_not_is_valid_type_with_invalid_name():
    assert mgr.is_valid_type("XRX120") == False
    
# todo: test_read_section_database()

def test_when_is_valid_section():
    # todo
    # create dataframe with simple keys
    # check that the string can be found
    pass

def test_when_not_is_valid_section():
    # todo
    # create dataframe with simple keys
    # check that the string can be found
    pass   

# todo: test_get_section_props()

def test_when_get_section_type_is_found():
    assert mgr.get_section_type("IPE100") == "IPE"
    
def test_when_get_section_type_is_not_found():
    assert mgr.get_section_type("LRB320") is None    

# todo: test_get_load_section_props()
# todo: test_get_section()

