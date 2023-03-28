
from eurocodedesign.units import (Newton,
                                  Meter,
                                  Meter_2,
                                  N, kN, m, MPa, J,
                                  Joule, Prefix)


class TestUnits:

    def test_addition_subtraction(self):
        a: Meter_2 = 3*Meter_2
        l: Meter = 2*m()
        assert l+l == 4*m()
        assert l-l == 0*m()
        assert l-l == 0
        assert l+0
        assert a+l, a-l

    def test_multiplication(self):
        l: Meter = Meter(5)
        f: Newton = N(3)
        a: Meter_2 = l*l
        assert a == 25*m()
        e: Joule = 15*J()
        assert (l*f) == e

    def test_division(self):
        e: J = 15 * J()
        a: Meter_2 = 5*Meter_2()
        l: Meter = 3*m()
        f: kN = 3*N()
        assert (e/f) == l
        assert (e/l) == f
        assert e/10 == 1.5*J()
        assert e/a == 3*MPa()

    def test_comparison(self):
        l1 = 1*m()
        l2 = 2*m()
        l3 = 1*m()
        assert l1 == l3
        assert l1 <= l2
        assert l1 < l2
        assert l2 > l1
        assert l2 >= l1
        assert l1 != l2
        assert l1 == 1

    def test_str(self):
        f: Newton = 1.3*kN()
        assert str(f) == ""
        f.to(Prefix.none)
        assert str(f) == ""
