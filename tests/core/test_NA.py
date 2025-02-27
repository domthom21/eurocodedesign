import pytest

from eurocodedesign.core import NA
from eurocodedesign.standard import ec3


def test_NA():
    de = NA.NACountry.DE
    assert ec3.gamma_M1() == 1.00
    assert float(NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1',
                                     country=de)) == 1.10
    assert ec3.gamma_M1() == 1.00
    NA.set_country(country=de)
    assert ec3.gamma_M0() == 1.00
    assert ec3.gamma_M1() == 1.10
    assert ec3.gamma_M2() == 1.25
    NA.set_country()
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with NA.CountryContext(country=de):
        assert ec3.gamma_M0() == 1.00
        assert ec3.gamma_M1() == 1.10
        assert ec3.gamma_M2() == 1.25
    assert ec3.gamma_M0() == 1.0
    assert ec3.gamma_M1() == 1.0
    assert ec3.gamma_M2() == 1.25
    with pytest.raises(NotImplementedError):
        with NA.CountryContext(country=de):
            NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M10')
    with pytest.raises(AttributeError):
        with NA.CountryContext(country=NA.NACountry.EN):
            NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1')
