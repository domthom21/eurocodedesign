import pytest
from pytest import approx

from eurocodedesign.standard.ec3.platebuckling import PlateSupport
import eurocodedesign.standard.ec3.platebuckling.effective_width_method as ewm
from eurocodedesign.units import mm, N, mm2


def test_longitudinal():
    assert (ewm.calc_bar_lambda_p(1000*mm(), 10*mm(), 0.81, 4.0)
            == approx(2.17, 0.01))
    assert (ewm.calc_rho(PlateSupport.TWO_SIDE, 2.17, 1.0)
            == approx(0.414, 0.001))
    assert (ewm.calc_sigma_crp(4.0, 19000*(10/1000)**2*N()/mm2())
            == approx(76*N()/mm2(), 0.1*N()/mm2()))

def test_buckling_like():
    #assert (ewm.calc_sigma_crc(10*mm(), 600*mm())
    #        == approx(53*N()/mm2()))
    assert (ewm.calc_xi(76, 53)
            == approx(0.44, 0.02))
