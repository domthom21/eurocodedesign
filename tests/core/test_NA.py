import pytest

import eurocodedesign as ed
import eurocodedesign.core.NA
from eurocodedesign.standard import ec3


def test_NA():
    assert ec3.gamma_M1() == 1.00
    assert float(ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1',
                                     country='de')) == 1.10
    assert ec3.gamma_M1() == 1.00
    ed.core.NA.set_country(country='de')
    assert ec3.gamma_M0() == 1.00
    assert ec3.gamma_M1() == 1.10
    assert ec3.gamma_M2() == 1.25
    ed.core.NA.set_country(None)
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with ed.core.NA.CountryContext(country='de'):
        assert ec3.gamma_M0() == 1.00
        assert ec3.gamma_M1() == 1.10
        assert ec3.gamma_M2() == 1.25
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with pytest.raises(NotImplementedError):
        with ed.core.NA.CountryContext(country='de'):
            ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M10')
    with pytest.raises(NotImplementedError):
        with ed.core.NA.CountryContext(country='ne'):
            ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1')
