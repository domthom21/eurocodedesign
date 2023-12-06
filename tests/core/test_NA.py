import pytest

import eurocodedesign as ed
import eurocodedesign.core.NA
from eurocodedesign.standard import ec3


def test_NA():
    de = ed.core.NA.NACountry.DE
    assert ec3.gamma_M1() == 1.00
    assert float(ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1',
                                     country=de)) == 1.10
    assert ec3.gamma_M1() == 1.00
    ed.core.NA.set_country(country=de)
    assert ec3.gamma_M0() == 1.00
    assert ec3.gamma_M1() == 1.10
    assert ec3.gamma_M2() == 1.25
    ed.core.NA.set_country()
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with ed.core.NA.CountryContext(country=de):
        assert ec3.gamma_M0() == 1.00
        assert ec3.gamma_M1() == 1.10
        assert ec3.gamma_M2() == 1.25
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with pytest.raises(NotImplementedError):
        with ed.core.NA.CountryContext(country=de):
            ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M10')
    with pytest.raises(AttributeError):
        with ed.core.NA.CountryContext(country=ed.core.NA.NACountry.EN):
            ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1')
