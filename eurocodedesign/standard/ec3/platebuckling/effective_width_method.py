from typing import NoReturn

import numpy as np

from eurocodedesign.core.typing import MeterTriple, Eta
from eurocodedesign.materials.structuralsteel import BasicStructuralSteel
import eurocodedesign.standard.ec3 as ec3
from eurocodedesign.standard.ec3 import platebuckling
from eurocodedesign.standard.ec3.crosssection.classification import \
    calc_epsilon
from eurocodedesign.standard.ec3.platebuckling import PlateSupport, \
    PlateStiffeners, get_eta
from eurocodedesign.units import Meter, Pascal, Newton, N, mm2, Meter_2, \
    Newtonmeter, Meter_3


def calc_bar_lambda_p(f_y: Pascal, sigma_crp: Pascal):
    """

    Args:
        f_y: yield strength :math:`f_y`
        sigma_crp: critical stress :math:`\sigma_{cr,p}` for plate buckling

    Returns: Relative slenderness :math:`\\bar{\lambda}_p` for plate buckling

    """
    bar_lambda_p = np.sqrt(f_y / sigma_crp)
    return bar_lambda_p


# bar b according to EN 1993-1-1 Tab. 5.2

def calc_bar_lambda_p(bar_b: Meter,
                      t: Meter,
                      epsilon: float,
                      k_sigmap: float) -> float:
    """

    Calculation according to EN 1993-1-5:2010-12 §4.4(2)

    Args:
        bar_b: Decisive width :math:`\bar{b}`,
        see also EN 1993-1-1:2010-12 Tab. 5.2
        t: Plate thickness :math:`t`
        epsilon: Epsilon factor :math:`\epsilon`, see
        :meth:`ec3.crosssection.classification.calc_epsilon`
        k_sigmap: plate buckling factor :math:`k_{\sigma,p}`, see calc_k_sigmap

    Returns: Relative plate slenderness :math:`\\bar{\lambda}_p`

    """
    bar_lambda_p = (bar_b / t) / (28.4 * epsilon * np.sqrt(k_sigmap))
    return bar_lambda_p


def calc_rho(support: PlateSupport,  # todo rename to rho_p?
             bar_lambda_p: float,
             psi: float = 1.0) -> float:
    """Calculates the reduction factor :math:`\\rho`

    Calculation for longitudinal plate buckling and two side supported or one
     side supported buckling plates without stiffeners.

    Calculation according to EN 1993-1-5:2019-10 §4.4.

    Args:
        support: PlateSupport.ONE_SIDE or PlateSupport.TWO_SIDE
        bar_lambda_p: relative slenderness :math:`\bar{\lambda}_p` for
        plate buckling, see calc_bar_lambda_p
        psi: stress ratio :math:`\psi`

    Returns:
        float: reduction factor :math:`\rho` for longitudinal plate buckling
    """
    if not isinstance(support, PlateSupport):
        raise TypeError('support must be an instance of Enum PlateSupport')

    if support == PlateSupport.ONE_SIDE:
        min_bar_lambda_p = 0.748
    if support == PlateSupport.TWO_SIDE:
        min_bar_lambda_p = 0.5 + np.sqrt(0.085 - 0.055 * psi)
    if bar_lambda_p <= min_bar_lambda_p:
        rho = 1.0
    else:  # bar_lambda_p > min_bar_lambda_p
        if support == PlateSupport.ONE_SIDE:
            rho = np.divide(bar_lambda_p - 0.188, bar_lambda_p ** 2)
        elif support == PlateSupport.TWO_SIDE:
            rho = np.divide(bar_lambda_p - 0.055 * (3 + psi),
                            bar_lambda_p ** 2)
        rho = 1.0 if rho > 1.0 else rho
    return rho


def calc_k_sigmap(psi: float, support: PlateSupport) -> float:
    """
    Calculate plate buckling facotr for Two-side supported plate

    One-side supported plate not supported!

    Calculation according to EN 1993-1-5:2019-10 Tab 4.1

    Args:
        psi: Stress ratio :math:`\psi = \sigma_2/\sigma_1`
        support: PlateSupport type

    Returns: plate buckling factor :math:`k_\sigma`

    """
    if support != PlateSupport.TWO_SIDE:
        raise NotImplementedError("k_sigmap only supported for two-side"
                                  " supported plates")
    k_sigmap: float
    if psi >= 1.0:
        k_sigmap = 4.0
    elif 1.0 > psi >= 0.0:
        k_sigmap = 8.2 / (1.05 + psi)
    elif 0.0 > psi >= -1.0:
        k_sigmap = 7.81 - 6.29 * psi + 9.78 * psi ** 2
    elif -1.0 > psi >= -3:
        k_sigmap = 5.98 * (1 - psi) ** 2
    else:
        raise ValueError(f"Psi has value outside valid range (<-3): {psi}")
    return k_sigmap


def calc_sigma_E(t: Meter,
                 b: Meter) -> Pascal:
    """
    Calculate maximum elastic stress value :math:`\sigma_E` for the plate

    Calculation according to EN 1993-1-5:2019-10 §A.1(2) with
    E = 21_000 kN/cm² and v = 0,3

    Args:
        t: plate thickness :math:`t`
        b: plate width :math:`b` where pressure is applied

    Returns: maximum elastic stress :math:`\sigma_E`

    """
    sigma_E: Pascal = 190_000 * N() / mm2() * (t / b) ** 2
    return sigma_E


def calc_sigma_crp(k_sigmap: float, sigma_E: Pascal) -> Pascal:
    """

    Calculation according to EN 1993-1-5:2019-10 §A.1(2) with
    E = 21_000 kN/cm² and v = 0,3

    Args:
        k_sigmap: plate buckling factor :math:`k_\sigma`, see calc_k_sigmap
        sigma_E: maximum elastic stress :math:`\sigma_E`, see calc_sigma_E

    Returns: critical stress :math:`\sigma_{cr,p}` for plate buckling

    """
    sigma_crp = k_sigmap * sigma_E
    return sigma_crp


def calc_effective_width(psi: float,
                         rho: float,
                         bar_b: Meter) -> MeterTriple:
    """Calculate effective plate width

    Calculation according to EN 1993-1-5:2019-10 Tab. 4.1

    Args:
        psi: stress ratio :math:`\psi = \sigma_2 / \sigma_1`
        rho: reduction factor :math:`\rho` for plate buckling, see calc_rho # todo rename to rho_p?
        bar_b:

    Returns: :math:`(b_{eff}, b_{e1}, b_{e2})`

    """
    b_eff: Meter
    b_e1: Meter
    b_e2: Meter
    if psi == 1.0:
        b_eff = rho * bar_b
        b_e1 = b_e2 = 0.5 * b_eff
    elif 1.0 > psi >= 0.0:
        b_eff = rho * bar_b
        b_e1 = 2.0 / (5.0 - psi) * b_eff
        b_e2 = b_eff - b_e1
    elif psi < 0.0:
        b_eff = rho * bar_b / (1.0 - psi)
        b_e1 = 0.4 * b_eff
        b_e2 = 0.6 * b_eff
    return b_eff, b_e1, b_e2


# flexural buckling of the compression flange
def calc_sigma_crc(t: Meter,
                   a: Meter) -> Pascal:  # E: modulus of elasticity = 210 000 N/mm², v=0,3 Poisson's ratio in elastic range, t: thickness
    """

    Calculation according to EN 1993-1-5:2019-10 $4.5.3(2) and §A.1(2) with
    E = 21_000 kN/cm² and v = 0,3

    Args:
        t: plate thickness :math:`t`
        a: plate (flange) length :math:`a`

    Returns: critical stress for flexural buckling of the flange
    :math:`\sigma_{cr,c}`

    """
    sigma_crc: Pascal = calc_sigma_E(t, a)
    return sigma_crc


def calc_bar_lambda_c(f_y: Pascal, sigma_crc: Pascal):  # TODO eq 4.10
    """
    Calculate the relative slenderness for flexural flange buckling

    Calculation according to EN 1993-1-5:2019-10 §4.5.3(4)

    Args:
        f_y: yield stress :math:`f_y`
        sigma_crc: critical stress :math:`\sigma_{cr,c}`
         for flexural flange buckling

    Returns: relative slenderness for flexural flange buckling
     :math:`\\bar{\\lambda_c}`

    """
    bar_lambda_c = np.sqrt(f_y / sigma_crc)
    return bar_lambda_c


# buckling line
def calc_chi_c(bar_lambda_c: float) -> float:  # see 4.5.3(5)
    r"""

    Calculates the reduction factor :math:`\chi_c` for lateral buckling-like behavior

    Calculation according to EN 1993-1-5:2019-10 §4.5.3(5) and
     EN 1993-1-1:2010-12 §6.3.1.2

    Args:
        bar_lambda_c: relative slenderness :math:`\bar{\lambda}_c`
        of the compression flange

    Returns: reduction factor :math:`\chi_c`

    """
    chi_c: float = ec3.buckling.calc_chi(bar_lambda_c,
                                         ec3.buckling.BucklingLine.a)
    return chi_c


def calc_xi(sigma_crp, sigma_crc) -> float:
    r"""
    Calculate the interaction factor between plate buckling and flange buckling

    Calculation according to EN 1993-1-5:2019-10 §4.5.4(1)

    Args:
        sigma_crp: critical stress :math:`\sigma_{cr,p}` for plate buckling
        sigma_crc: critical stress :math:`\sigma_{cr,c}` for buckling of the compression flange

    Returns: interaction factor :math:`\xi`

    """
    xi = np.clip(sigma_crp / sigma_crc - 1.0, 0.0, 1.0)
    return xi


def calc_rho_c(rho: float, chi_c: float,
               xi: float) -> float:  # todo rename rho_p?
    r"""

    Args:
        rho: reduction factor :math:`\rho` for plate buckling, see calc_rho
        chi_c: reduction factor :math:`\chi_c` for compression flange buckling,
            see calc_chi_c
        xi: interaction factor :math:`\xi`, see calc_xi

    Returns: final reduction factor :math:`\rho_c`

    """
    rho_c = (rho - chi_c) * xi * (2 - xi) + chi_c
    return rho_c


# todo calc eta
def calc_eta_1(f_y: Pascal, N_Ed: Newton, A_eff: Meter_2,
               M_y_Ed: Newtonmeter, e_yN: Meter, W_yeff: Meter_3,
               M_z_Ed: Newtonmeter, e_zN: Meter, W_zeff: Meter_3) -> Eta:
    r"""
    eta_1 for plate buckling with effective width method

    Valid for axial force and two axial bending moment

    Calculation according to EN 1993-1-5:2019-10 §4.6(1)

    Args:
        f_y: yield stress :math:`f_y`
        N_Ed: design value :math:`N_{Ed}` of the compression axial force
        A_eff: effective area :math:`A_{eff}` of the cross-section
        M_y_Ed: design value :math:`M_{y,Ed}` of the bending moment
         about y-y axis
        e_yN: shift of the centroid :math:`e_{y,N}` of the effective area
         :math:`A_{eff}` relative to the centroid of the gross cross-section,
          resulting in a bending moment about y-y axis
        W_yeff: effective section modulus :math:`W_{y,eff}` about y-y axis
        M_z_Ed: design value :math:`M_{z,Ed}` of the bending moment
        about z-z axis
        e_zN: shift of the centroid :math:`e_{z,N}` of the effective area
         :math:`A_{eff}` relative to the centroid of the gross cross-section,
          resulting in a bending moment about z-z axis
        W_zeff: effective section modulus :math:`W_{z,eff}` about z-z axis

    Returns: load factor :math:`\eta_1` by effective width method

    """
    eta_1 = (N_Ed / (f_y * A_eff / ec3.gamma_M0())
             + (M_y_Ed + N_Ed * e_yN) / (f_y * W_yeff / ec3.gamma_M0())
             + (M_z_Ed + N_Ed * e_zN) / (f_y * W_zeff / ec3.gamma_M0()))
    return eta_1


########## Shear buckling #############
# For shear buckling resistance, EN 1993-1-5 covers panels
# supported on four edges only.

# according to EC3-1-5 and EC3-1-1 8.2.6(6)
def is_shear_buckling_verification_required(h_w: Meter,
                                            t: Meter,
                                            steel_grade: BasicStructuralSteel,
                                            stiffeners: PlateStiffeners) \
                                            -> bool:
    # lexicographic comparison
    eta: float = platebuckling.get_eta(steel_grade)
    epsilon: float = calc_epsilon(steel_grade.f_yk)

    if stiffeners == PlateStiffeners.NONE:
        return h_w / t > 72 / eta * epsilon
    else:
        raise NotImplementedError("Not implemented for stiffened plates")


# see eq a.5
def calc_k_tau(h_w: Meter, a: Meter, stiffeners: PlateStiffeners) -> float:
    if PlateStiffeners != PlateStiffeners.NONE:
        raise NotImplementedError("Not implemented for stiffeners")
    k_tau: float
    if a / h_w >= 1.0:
        k_tau = 5.34 + 4.2 * (h_w / a) ** 2
    else:  # a / h_w < 1.0
        k_tau = 4.00 + 5.34 * (h_w / a) ** 2
    return k_tau


# see eq 5.4
def calc_tau_cr(k_tau: float, sigma_E: Pascal) -> Pascal:
    t_cr = k_tau * sigma_E


# according to eq 5.3
def calc_bar_lambda_w(f_yw: Pascal, tau_cr: Pascal) -> float:
    bar_lambda_w = 0.76 * np.sqrt(f_yw / tau_cr)
    return bar_lambda_w


def calc_chi_w(bar_lambda_w: float,
               steel_grade: BasicStructuralSteel,
               stiffeners: PlateStiffeners) -> float:
    eta: float = ec3.platebuckling.get_eta(steel_grade)
    chi_w: float
    if bar_lambda_w < 0.83 / eta:
        chi_w = eta
    elif 0.83 / eta <= bar_lambda_w < 1.08:
        chi_w = 0.83 / bar_lambda_w
    else:  # bar_lambda_w >= 1.08
        if stiffeners == PlateStiffeners.RIGID:
            chi_w = 1.37 / (0.7 + bar_lambda_w)
        else:  # non-rigid or none
            chi_w = 0.83 / bar_lambda_w
    return chi_w


def calc_V_bw_Rd(chi_w: float, f_yw: Pascal, h_w: Meter,
                 t: Meter) -> Newton:  # 5.2
    V_bw_Rd: Newton = (chi_w * f_yw * h_w * t) / (np.sqrt(3) * ec3.gamma_M1())
    return V_bw_Rd


def calc_V_bf_Rd() -> NoReturn:
    raise NotImplementedError  # 5.4, eq. 5.8


def calc_V_b_Rd(V_bw_Rd: Newton,
                V_bf_Rd: Newton,
                steel_grade: BasicStructuralSteel,
                f_yw: Pascal,
                h_w: Meter,
                t: Meter) -> Newton:
    eta: float = get_eta(steel_grade)
    V_b_Rd: Newton = V_bw_Rd + V_bf_Rd
    max_V_b_Rd: Pascal = (eta * f_yw * h_w * t) / (np.sqrt(3) * ec3.gamma_M1())
    return min(V_b_Rd, max_V_b_Rd)


def calc_eta_3(V_Ed: Pascal, V_bw_Rd: Pascal) -> Eta:
    eta_3: Eta = V_Ed / V_bw_Rd
    return eta_3
