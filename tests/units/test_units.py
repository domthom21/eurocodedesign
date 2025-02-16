import pytest
from eurocodedesign.units import (Newton,
                                  Meter,
                                  Meter_2,
                                  N, kN, m, m2, cm, cm2, Pa, J,
                                  Joule, Prefix)


class TestUnits:

    def test_unit_to_numeric(self):
        f: kN = 2*kN()
        assert f.to_numeric() == 2000.0

    def test_addition_subtraction(self):
        a: Meter_2 = 3*Meter_2()
        l: Meter = 2*m()
        assert l+l == 4*m()
        assert l-l == 0*m()
        with pytest.raises(TypeError):
            l+0
        with pytest.raises(TypeError):
            a+l, a-l

    def test_multiplication(self):
        l: Meter = Meter(5)
        f: Newton = N(3)
        a: Meter_2 = l*l
        assert a == 25*m2()
        e: Joule = 15*J()
        assert (l*f) == e
        assert l*5 == 25*m()

    def test_division(self):
        e: J = 15 * J()
        a: Meter_2 = 5*Meter_2()
        l: Meter = 5*m()
        f: kN = 3*N()
        assert (e/f) == l
        assert (e/l) == f
        assert e/10 == 1.5*J()
        assert 15*N()/a == 3*Pa()
        with pytest.raises(ZeroDivisionError):
            e/0
        with pytest.raises(ZeroDivisionError):
            e/(0*J())
        assert e/(15*J()) == 1.0

    def test_comparison(self):
        l1 = 1*m()
        l2 = 2*m()
        l3 = 100*cm()
        assert l1 == l3
        assert l1 <= l2
        assert l1 < l2
        assert l2 > l1
        assert l2 >= l1
        assert l1 != l2
        with pytest.raises(TypeError):
            l1 == 1

    def test_to_str(self):
        f: Newton = 1.3*kN()
        assert str(f) == r'1.3 kN'
        f.to(Prefix.none)
        assert str(f) == r'1300.0 N'
        a: m2 = 100*cm2()
        assert str(a) == r'100.0 cm²'
