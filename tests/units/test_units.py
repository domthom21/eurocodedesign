import pytest

from eurocodedesign.units import (Newton,
                                  Meter,
                                  Meter_2,
                                  N, m, m2, Pa, J,
                                  Joule, Prefix)


class TestUnits:

    def test_unit_to_numeric(self):
        f: N = 2*Prefix.k*N(1)
        assert f == 2000.0

    def test_addition_subtraction(self):
        a: Meter_2 = 3*Meter_2()
        l: Meter = 2*m()
        assert l+l == 4*m()
        assert l-l == 0*m()

    def test_multiplication(self):
        l: Meter = Meter(5)
        f: Newton = N(3)
        a: Meter_2 = l*l
        assert a == 25*m2(1)
        e: Joule = 15*J(1)
        assert (l*f) == e
        assert l*5 == 25*m(1)

    def test_division(self):
        e: J = 15 * J(1)
        a: Meter_2 = 5*Meter_2(1)
        l: Meter = 5*m(1)
        f: N = 3*N(1)
        assert (e/f) == l
        assert (e/l) == f
        assert e/10 == 1.5*J(1)
        assert 15*N(1)/a == 3*Pa(1)
        with pytest.raises(ZeroDivisionError):
            e/0
        with pytest.raises(ZeroDivisionError):
            e/(0*J())
        assert e/(15*J(1)) == 1.0

    def test_comparison(self):
        l1 = 1*m(1)
        l2 = 2*m(1)
        l3 = 100*(Prefix.centi)*m(1)
        assert l1 == l3
        assert l1 <= l2
        assert l1 < l2
        assert l2 > l1
        assert l2 >= l1
        assert l1 != l2

    def test_to_str(self):
        f: Newton = 1.3*Prefix.k*N(1)
        assert str(f) == r'1300.0'
        a: m2 = 100*Prefix.c**2*m2(1)
        assert str(a) == r'0.01'
