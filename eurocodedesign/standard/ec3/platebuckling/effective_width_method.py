"""
Methods for plate buckling verification by effective width method

Plate buckling methods from EN 1993-1-5:2019-10 §4-9

Currently supports mainly two-side supported plates without stiffeners

For shear buckling resistance, EN 1993-1-5 covers panels supported
on four edges only.
"""

from functools import singledispatch
from typing import NoReturn, Any

import numpy as np

from eurocodedesign.core.typing import MeterTriple, Eta
from eurocodedesign.materials.structuralsteel import BasicStructuralSteel
import eurocodedesign.standard.ec3 as ec3
from eurocodedesign.standard.ec3 import platebuckling, buckling # noqa: F401
from eurocodedesign.standard.ec3.crosssection.classification import \
    calc_epsilon
from eurocodedesign.standard.ec3.platebuckling import PlateSupport, \
    PlateStiffeners
from eurocodedesign.units import Meter, Pascal, Newton, N, mm2, Meter_2, \
    Newtonmeter, Meter_3


@singledispatch
def calc_bar_lambda_p(*args: Any) -> float:
    r"""Calculate modified slenderness for plate buckling

       Calculation according to EN 1993-1-5:2019-10 §4.4(2)

       args is either yield strength :math:`f_y` and critical stress
       :math:`\sigma_{cr,p}` for plate buckling or
       decisive width :math:`\bar{b}`, plate thickness :math:`t`,
       epsilon factor :math:`\epsilon` and  plate buckling factor
        :math:`k_{\sigma,p}

       Args:
           f_y: yield strength :math:`f_y`
           sigma_crp: critical stress :math:`\sigma_{cr,p}` for plate buckling
           bar_b: decisive width :math:`\bar{b}`,
            see also EN 1993-1-1:2010-12 Tab. 5.2
           t: plate thickness :math:`t`
           epsilon: epsilon factor :math:`\epsilon`, see
            ec3.crosssection.classification.calc_epsilon
           k_sigmap: plate buckling factor :math:`k_{\sigma,p}`,
            see calc_k_sigmap

       Returns: Relative slenderness :math:`\bar{\lambda}_p` for plate buckling

    """
    raise NotImplementedError(f"calc_bar_lambda_p not supported for "
                              f"argument type {type(args)}")


@calc_bar_lambda_p.register
def _calc_bar_lambda_p_f_y(f_y: Pascal, sigma_crp: Pascal) -> float:
    r"""Calculate modified slenderness for plate buckling

    Calculation according to EN 1993-1-5:2019-10 §4.4(2)

    Args:
        f_y: yield strength :math:`f_y`
        sigma_crp: critical stress :math:`\sigma_{cr,p}` for plate buckling

    Returns: Relative slenderness :math:`\bar{\lambda}_p` for plate buckling

    """
    bar_lambda_p: float = np.sqrt(f_y / sigma_crp)
    return bar_lambda_p


@calc_bar_lambda_p.register
def _calc_bar_lambda_p_bar_b(bar_b: Meter,
                             t: Meter,
                             epsilon: float,
                             k_sigmap: float) -> float:
    r"""Calculate modified slenderness for plate buckling

    Calculation according to EN 1993-1-5:2019-10 §4.4(2)

    Args:
        bar_b: Decisive width :math:`\bar{b}`,
            see also EN 1993-1-1:2010-12 Tab. 5.2
        t: Plate thickness :math:`t`
        epsilon: Epsilon factor :math:`\epsilon`, see
            ec3.crosssection.classification.calc_epsilon
        k_sigmap: plate buckling factor :math:`k_{\sigma,p}`, see calc_k_sigmap

    Returns: Relative plate slenderness :math:`\bar{\lambda}_p`

    """
    bar_lambda_p: float = (bar_b / t) / (28.4 * epsilon * np.sqrt(k_sigmap))
    return bar_lambda_p


def calc_rho_p(support: PlateSupport,
               bar_lambda_p: float,
               psi: float = 1.0) -> float:
    r"""Calculates the reduction factor :math:`\rho_p` for plate buckling

    Calculation for longitudinal plate buckling and two side supported or one
     side supported buckling plates without stiffeners.

    Calculation according to EN 1993-1-5:2019-10 §4.4(2).

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
        rho_p = 1.0
    else:  # bar_lambda_p > min_bar_lambda_p
        if support == PlateSupport.ONE_SIDE:
            rho_p = (bar_lambda_p - 0.188) / (bar_lambda_p ** 2)
        elif support == PlateSupport.TWO_SIDE:
            rho_p = (bar_lambda_p - 0.055 * (3 + psi)) / (bar_lambda_p ** 2)
        else:
            raise ValueError(f"Invalid value for PlateSupport: {support}")
    return rho_p


def calc_k_sigmap(psi: float, support: PlateSupport) -> float:
    r"""Calculate plate buckling factor for two-side supported plate

    One-side supported plate not supported.

    Calculation according to EN 1993-1-5:2019-10 Tab 4.1

    Args:
        psi: Stress ratio :math:`\psi = \sigma_2/\sigma_1`
        support: PlateSupport type

    Returns: plate buckling factor :math:`k_\sigma`

    """
    if support != PlateSupport.TWO_SIDE:
        raise NotImplementedError("calc_k_sigmap only supported for two-side"
                                  " supported plates")
    k_sigmap: float
    if psi == 1.0:
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
    r"""Calculate maximum elastic stress value :math:`\sigma_E` for the plate

    Calculation according to EN 1993-1-5:2019-10 §A.1(2) with
    E = 21_000 kN/cm² and v = 0,3

    Args:
        t: plate thickness :math:`t`
        b: plate width :math:`b` where the pressure is applied

    Returns: maximum elastic stress :math:`\sigma_E`

    """
    sigma_E: Pascal = 190_000 * N() / mm2() * (t / b) ** 2
    return sigma_E


def calc_sigma_crp(k_sigmap: float, sigma_E: Pascal) -> Pascal:
    r"""Calculate critical stress :math:`\sigma_{cr,p}` for plate buckling

    Calculation according to EN 1993-1-5:2019-10 §A.1(2) with
    E = 21_000 kN/cm² and v = 0,3

    Args:
        k_sigmap: plate buckling factor :math:`k_\sigma`, see calc_k_sigmap
        sigma_E: maximum elastic stress :math:`\sigma_E`, see calc_sigma_E

    Returns: critical stress :math:`\sigma_{cr,p}` for plate buckling

    """
    sigma_crp = k_sigmap * sigma_E
    return sigma_crp


def calc_effective_width(support: PlateSupport,
                         bar_b: Meter,
                         rho_p: float,
                         psi: float) -> MeterTriple:
    r"""Calculate effective plate widths :math:`(b_{eff}, b_{e1}, b_{e2})`

    Calculation according to EN 1993-1-5:2019-10 Tab. 4.1

    Only implemented for two-side supported plates.

    Args:
        bar_b: Decisive width :math:`\bar{b}`
        rho_p: reduction factor :math:`\rho` for plate buckling, see calc_rho_p
        psi: stress ratio :math:`\psi = \sigma_2 / \sigma_1`

    Returns: Effective plate widths :math:`(b_{eff}, b_{e1}, b_{e2})`

    """
    if support != PlateSupport.TWO_SIDE:
        raise NotImplementedError("calc_effective_width only implemented for"
                                  "two-side supported plates")
    b_eff: Meter
    b_e1: Meter
    b_e2: Meter
    if psi == 1.0:
        b_eff = rho_p * bar_b
        b_e1 = b_e2 = 0.5 * b_eff
    elif 1.0 > psi >= 0.0:
        b_eff = rho_p * bar_b
        b_e1 = 2.0 / (5.0 - psi) * b_eff
        b_e2 = b_eff - b_e1
    elif psi < 0.0:
        b_eff = rho_p * bar_b / (1.0 - psi)
        b_e1 = 0.4 * b_eff
        b_e2 = 0.6 * b_eff
    return b_eff, b_e1, b_e2


def calc_sigma_crc(t: Meter,
                   a: Meter) -> Pascal:
    r"""Calculate critical stress value :math:`\sigma_{cr,c}`

    Due to flexural buckling of the compression flange for unstiffened plates

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


def calc_bar_lambda_c(f_y: Pascal, sigma_crc: Pascal) -> float:
    r"""Calculate the relative slenderness for flexural flange buckling

    Calculation according to EN 1993-1-5:2019-10 §4.5.3(4)

    Args:
        f_y: yield stress :math:`f_y`
        sigma_crc: critical stress :math:`\sigma_{cr,c}`
         for flexural flange buckling, see calc_sigma_crc

    Returns: relative slenderness for flexural flange buckling
     :math:`\bar{\lambda_c}`

    """
    bar_lambda_c: float = np.sqrt(f_y / sigma_crc)
    return bar_lambda_c


def calc_chi_c(stiffeners: PlateStiffeners,
               bar_lambda_c: float) -> float:
    r"""Calculate the reduction factor :math:`\chi_c` for lateral buckling-like
     behavior

    Calculation according to EN 1993-1-5:2019-10 §4.5.3(5) and
     EN 1993-1-1:2010-12 §6.3.1.2

    Not implemented for stiffened plates

    Args:
        bar_lambda_c: relative slenderness :math:`\bar{\lambda}_c`
        of the compression flange

    Returns: reduction factor :math:`\chi_c`

    """
    if stiffeners != PlateStiffeners.NONE:
        raise NotImplementedError("calc_chi_c only implemented "
                                  "for unstiffened plates")

    chi_c: float = ec3.buckling.calc_chi(bar_lambda_c,
                                         ec3.buckling.BucklingLine.a)
    return chi_c


def calc_xi(sigma_crp: Pascal, sigma_crc: Pascal) -> float:
    r"""
    Calculate the interaction factor :math:`\xi` between plate and
     flange buckling

    Calculation according to EN 1993-1-5:2019-10 §4.5.4(1)

    Args:
        sigma_crp: critical stress :math:`\sigma_{cr,p}` for plate buckling
        sigma_crc: critical stress :math:`\sigma_{cr,c}` for buckling of the
            compression flange

    Returns: interaction factor :math:`\xi`

    """
    xi: float = np.clip(sigma_crp / sigma_crc - 1.0, 0.0, 1.0)
    return xi


def calc_rho_c(rho_p: float, chi_c: float,
               xi: float) -> float:
    r"""Calculate reduction factor :math:`\rho_c`

    Due to interaction of plate buckling and buckling

    Calculation according to EN 1993-1-5:2019-10 §4.5.4(1)

    Args:
        rho_p: reduction factor :math:`\rho_p` for plate buckling,
            see calc_rho_p
        chi_c: reduction factor :math:`\chi_c` for compression flange buckling,
            see calc_chi_c
        xi: interaction factor :math:`\xi`, see calc_xi

    Returns: final reduction factor :math:`\rho_c`

    """
    rho_c = (rho_p - chi_c) * xi * (2 - xi) + chi_c
    return rho_c


def calc_eta_1(f_y: Pascal,
               N_Ed: Newton,
               A_eff: Meter_2,
               M_y_Ed: Newtonmeter = 0*Newtonmeter(),
               W_yeff: Meter_3 = np.infty*Meter_3(),
               e_yN: Meter = 0*Meter(),
               M_z_Ed: Newtonmeter = 0*Newtonmeter(),
               W_zeff: Meter_3 = np.infty*Meter_3(),
               e_zN: Meter = 0*Meter()) -> Eta:
    r"""
Utilisation rate :math:`\eta_1` for plate buckling with effective width method

    Valid for axial force and biaxial bending moments

    Calculation according to EN 1993-1-5:2019-10 §4.6(1)

    Args:
        f_y: yield stress :math:`f_y`
        N_Ed: design value :math:`N_{Ed}` of the compression axial force
        A_eff: effective area :math:`A_{eff}` of the cross-section
        M_y_Ed: design value :math:`M_{y,Ed}` of the bending moment
         about y-y axis
        W_yeff: effective section modulus :math:`W_{y,eff}` about y-y axis
        e_yN: shift of the centroid :math:`e_{y,N}` of the effective area
         :math:`A_{eff}` relative to the centroid of the gross cross-section,
         resulting in a bending moment about y-y axis
        M_z_Ed: design value :math:`M_{z,Ed}` of the bending moment
         about z-z axis
        W_zeff: effective section modulus :math:`W_{z,eff}` about z-z axis
        e_zN: shift of the centroid :math:`e_{z,N}` of the effective area
         :math:`A_{eff}` relative to the centroid of the gross cross-section,
         resulting in a bending moment about z-z axis

    Returns: utilisation rate :math:`\eta_1` by effective width method

    """
    eta_1: Eta = ((N_Ed / (f_y * A_eff / ec3.gamma_M0()))
                  + (M_y_Ed + N_Ed * e_yN) / (f_y * W_yeff / ec3.gamma_M0())
                  + (M_z_Ed + N_Ed * e_zN) / (f_y * W_zeff / ec3.gamma_M0()))
    return eta_1


def is_shear_buckling_verification_required(h_w: Meter,
                                            t_w: Meter,
                                            steel_grade: BasicStructuralSteel,
                                            stiffeners: PlateStiffeners) \
                                            -> bool:
    r"""Check if shear buckling verification is required

    Only non-stiffened plates are supported which are supported on four edges.
    Calculation according to EN 1993-1-5:2019-10 §5.1(2)

    Args:
        h_w: web height :math:`h_w`  from flange to flange
        t_w: web thickness :math:`t_w`
        steel_grade: steel grade, see eurocodedesign.materials.structuralsteel
        stiffeners: stiffeners on the plate

    Returns: True, if shear buckling verification is required

    """
    eta: float = platebuckling.get_eta(steel_grade)
    epsilon: float = calc_epsilon(steel_grade.f_yk)

    if stiffeners == PlateStiffeners.NONE:
        return h_w / t_w > 72 / eta * epsilon
    else:
        raise NotImplementedError("Not implemented for stiffened plates")


def calc_k_tau(h_w: Meter, a: Meter, stiffeners: PlateStiffeners) -> float:
    r"""Calculate shear plate buckling factor :math:`k_\tau`

    According to EN 1993-1-5:2019-10 §A.3(1)

    Not implemented for stiffeners

    Args:
        h_w: Web height :math:`h_w`
        a: Distance :math:`a` between lateral stiffeners
        stiffeners: Type of plate stiffening

    Returns: Shear plate buckling factor :math:`k_\tau`

    """
    if stiffeners != PlateStiffeners.NONE:
        raise NotImplementedError("Not implemented for stiffeners")
    k_tau: float
    if a / h_w >= 1.0:
        k_tau = 5.34 + 4.2 * (h_w / a) ** 2
    else:  # a / h_w < 1.0
        k_tau = 4.00 + 5.34 * (h_w / a) ** 2
    return k_tau


def calc_tau_cr(k_tau: float, sigma_E: Pascal) -> Pascal:
    """Calculate :math:`\tau_{cr}`

    According to EN 1993-1-5:2019-10 §5.3(3)

    Args:
        k_tau: shear plate buckling factor :math:`k_\tau`, see calc_k_tau
        sigma_E: yield stress :math:`sigma_E`, see calc_sigma_E

    Returns: Critical shear stress :math:`\tau_{cr}`

    """
    tau_cr = k_tau * sigma_E
    return tau_cr


def calc_bar_lambda_w(f_yw: Pascal, tau_cr: Pascal) -> float:
    r"""Calculate modified web slenderness :math:`\bar{\lambda}_w`

    According to EN 1993-1-5:2019-10 §5.3(3)

    Calculation by web height is currently not supported.

    Args:
        f_yw: yield stress :math:`f_yw` of the web
        tau_cr: critical shear stress :math:`\tau_{cr}`

    Returns: Modified web slenderness :math:`\bar{\lambda}_w`

    """
    bar_lambda_w: float = 0.76 * np.sqrt(f_yw / tau_cr)
    return bar_lambda_w


def calc_chi_w(bar_lambda_w: float,
               steel_grade: BasicStructuralSteel,
               stiffeners: PlateStiffeners) -> float:
    r"""Calculate shear buckling reduction factor :math:`\chi_w`

    According to EN 1993-1-5:2019-10 §5.3(1)

    Args:
        bar_lambda_w: modified web slenderness :math:`\bar{\lambda}_w`,
            see calc_bar_lambda_w()
        steel_grade: mteel grade, see eurocodedesign.materials.strucuralsteel
        stiffeners: type of plate stiffening

    Returns: reduction factor :math:`\chi_w` due to web (shear) buckling

    """
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
                 t_w: Meter) -> Newton:  # 5.2
    r"""Calculate design resistance :math:`V_{bw,Rd}` of the web

    According to EN 1993-1-5:2019-10 §5.2(1)

    Args:
        chi_w: web reduction factor :math:`\chi_w`, see calc_chi_w()
        f_yw: yield stress :math:`f_{yw}` of the web
        h_w: web height :math:`h_w` from flange to flange
        t_w: web thickness :math:`t_w`

    Returns: design resistance :math:`V_{bw,Rd}` of the web

    """
    V_bw_Rd: Newton = (chi_w * f_yw * h_w * t_w)/(np.sqrt(3) * ec3.gamma_M1())
    return V_bw_Rd


def calc_V_bf_Rd() -> NoReturn:
    """Design resistance of shear buckling resistance of the flange

    According to EN 1993-1-5:2019-10 §5.4

    Not implemented, yet.

    """
    raise NotImplementedError


def calc_V_b_Rd(V_bw_Rd: Newton,
                V_bf_Rd: Newton,
                steel_grade: BasicStructuralSteel,
                f_yw: Pascal,
                h_w: Meter,
                t_w: Meter) -> Newton:
    r"""Calculate the design value :math:`V_{b,Rd}` of the shear buckling
resistance

    According to EN 1993-1-5:2019-10 §5.2(1)

    Args:
        V_bw_Rd: design value of shear buckling resistance of the web
        V_bf_Rd: design value of shear buckling resistance of the flange
        steel_grade: steel grade
        f_yw: yield stress :math:`f_{yw}` of the web
        h_w: web height :math:`h_w`
        t_w: web thickness :math:`t_w`

    Returns: design value :math:`V_{b,Rd}` of the shear buckling resistance

    """
    eta: float = platebuckling.get_eta(steel_grade)
    V_b_Rd: Newton = V_bw_Rd + V_bf_Rd
    max_V_b_Rd: Newton = (eta * f_yw * h_w * t_w)/(np.sqrt(3) * ec3.gamma_M1())
    return min(V_b_Rd, max_V_b_Rd)


def calc_eta_3(V_Ed: Pascal, V_b_Rd: Pascal) -> Eta:
    r"""Calculate utilisation rate :math:`\eta_3` due to shear buckling

    According to EN 1993-1-5:2019-10 §5.5(1)

    Args:
        V_Ed: design value :math:`V_{Ed}` of shear force and torsion
        V_b_Rd: design value :math:`V_{b,Rd}` of shear buckling resistance

    Returns: utilisation rate :math:`\eta_3` due to shear force

    """
    eta_3: Eta = V_Ed / V_b_Rd
    return eta_3
