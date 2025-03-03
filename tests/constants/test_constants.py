import pytest

from eurocodedesign.constants import (N, m, m2, Pa, J, kN, cm, cm2)
from eurocodedesign.core.typing import Newton, Meter, Meter_2, Joule


class TestUnits:

    def test_unit_to_numeric(self):
        f: Newton = 2*kN
        assert f == 2000.0

    def test_addition_subtraction(self):
        a: Meter_2 = 3*m2
        l: Meter = 2*m
        assert l+l == 4*m
        assert l-l == 0*m

    def test_multiplication(self):
        l: Meter = 5*m
        f: Newton = 3*N
        a: Meter_2 = l*l
        assert a == 25*m2
        e: Joule = 15*J
        assert (l*f) == e
        assert l*5 == 25*m

    def test_division(self):
        e: J = 15 * J
        a: Meter_2 = 5*m2
        l: Meter = 5*m
        f: N = 3*N
        assert (e/f) == l
        assert (e/l) == f
        assert e/10 == 1.5*J
        assert 15*N/a == 3*Pa
        with pytest.raises(ZeroDivisionError):
            e/0
        with pytest.raises(ZeroDivisionError):
            e/(0*J)
        assert e/(15*J) == 1.0

    def test_comparison(self):
        l1 = 1*m
        l2 = 2*m
        l3 = 100*cm
        assert l1 == l3
        assert l1 <= l2
        assert l1 < l2
        assert l2 > l1
        assert l2 >= l1
        assert l1 != l2

    def test_to_str(self):
        f: Newton = 1.3*kN
        assert str(f) == r'1300.0'
        a: m2 = 100*cm2
        assert str(a) == r'0.01'
