from pytest import approx

from eurocodedesign.materials.structuralsteel import S355
from eurocodedesign.standard.ec3.platebuckling import PlateSupport, \
    PlateStiffeners
import eurocodedesign.standard.ec3.platebuckling.effective_width_method as ewm
from eurocodedesign.units import mm, N, mm2, kN, isclose


def test_longitudinal():
    assert (ewm.calc_k_sigmap(1.0, PlateSupport.TWO_SIDE)
            == approx(4.0))
    assert (ewm.calc_bar_lambda_p(1000 * mm(), 10 * mm(), 0.81, 4.0)
            == approx(2.17, 0.01))
    assert (ewm.calc_rho_p(PlateSupport.TWO_SIDE, 2.17, 1.0)
            == approx(0.414, 0.001))
    assert isclose(ewm.calc_sigma_crp(4.0, 190000 * (10 / 1000) ** 2
                                      * N() / mm2()), 76.00 * N() / mm2())


def test_buckling_like():
    assert isclose(ewm.calc_sigma_crc(10*mm(), 600*mm()), 52.7777777*N()/mm2())
    assert (ewm.calc_xi(109, 76)
            == approx(0.44, 0.02))
    assert (ewm.calc_bar_lambda_c(355 * N() / mm2(), 76 * N() / mm2())
            == approx(2.16, 0.01))
    assert (ewm.calc_chi_c(2.16)
            == approx(0.194, 0.01))
    assert (ewm.calc_rho_c(0.485, 0.194, 0.44)
            == approx(0.394, 0.001))
    # assert (ewm.calc_effective_width(2.16)
    #       == approx(0.194, 0.001))
    # assert (ewm.calc_eta_1(1000 * mm(), 10 * mm(), 0.81, 4.0)
    #        == approx(2.17, 0.01))


def test_shear_buckling():
    assert (ewm.get_eta(S355()) == approx(1.2))
    assert (ewm.is_shear_buckling_verification_required(1000 * mm(),
                                                        12 * mm(),
                                                        S355(),
                                                        PlateStiffeners.NONE)
            is True)
    assert (ewm.calc_k_tau(1000*mm(), 600*mm(), PlateStiffeners.NONE)
            == approx(18.833, 0.01))
    assert isclose(ewm.calc_tau_cr(18.833,
                                   ewm.calc_sigma_E(12*mm(),
                                                    1000*mm())),
                   515.270879*N()/mm2())
    assert (ewm.calc_bar_lambda_w(355*N()/mm2(), 515*N()/mm2())
            == approx(0.631, 0.01))
    assert (ewm.calc_chi_w(0.631, S355(), PlateStiffeners.NONE)
            == approx(1.20))
    assert isclose(ewm.calc_V_bw_Rd(1.096, 355 * N() / mm2(),
                                    1000*mm(),
                                    10*mm()),
                   2246354*N())
    assert (ewm.calc_eta_3(700*kN(), 2683*kN())
            == approx(0.261, 0.01))
