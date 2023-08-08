from pytest import approx
from math import inf

from eurocodedesign.standard.ec3.platebuckling import \
    reduced_stress_method as rsm
from eurocodedesign.standard.ec3.platebuckling.reduced_stress_method import \
    PlateSupport
from eurocodedesign.units import MPa


def test_is_permitted():
    assert rsm.is_permitted(rho=1.0, alpha_ultk=1.2) is True
    assert rsm.is_permitted(rho=0.8, alpha_ultk=1.0) is False


def test_calc_bar_lambda_p():
    assert rsm.calc_bar_lambda_p(alpha_ultk=1.392,
                                 alpha_cr=3.660) == approx(0.617, 0.001)


def test_calc_alpha_ultk():
    assert rsm.calc_alpha_ultk(f_y=355*MPa(),
                               sigma_x_Ed=245*MPa(),
                               sigma_z_Ed=0*MPa(),
                               tau_Ed=41*MPa()) == approx(1.392, 0.001)


def test_calc_alpha_cr():
    assert rsm.calc_alpha_cr(alpha_crx=4.203,
                             alpha_crz=inf,
                             alpha_crtau=10.178,
                             psi_x=1.0,
                             psi_z=0.0) == approx(3.660, 0.001)


def test_calc_rho():
    bar_lambda_p = 0.994
    assert rsm.calc_rho(method='interpolate',
                        support=PlateSupport.TWO_SIDE,
                        bar_lambda_p=bar_lambda_p,
                        psi_x=0.5,
                        psi_z=-3) == approx((0.811, 1.0, 1.0), 0.001)


def test_calc_eta():
    assert rsm.calc_eta(f_y=355*MPa(),
                        sigma_x_Ed=-231*MPa(),
                        sigma_z_Ed=13.6*MPa(),
                        tau_Ed=75*MPa(),
                        rho_x=1,
                        rho_z=0.941,
                        chi_w=1) == approx(0.5854668265)
