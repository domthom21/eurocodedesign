from typing import Literal, NoReturn

import numpy as np

from eurocodedesign.core.typing import FloatTriple, Eta
from eurocodedesign.standard.ec3 import gamma_M1
from eurocodedesign.standard.ec3.platebuckling import PlateSupport
from eurocodedesign.standard.ec3.platebuckling.effective_width_method import \
    calc_rho
from eurocodedesign.stepper import inject_stepper, Stepper
from eurocodedesign.units import Pascal


@inject_stepper
def is_permitted(rho: float, alpha_ultk: float, stepper: Stepper) -> bool:
    r"""Check prerequisites for the reduced stress method of plate buckling

    Calculation according to EN 1993-1-5:2019-10 §2.4, §10 (1) and §10 (2).

    The reduced stress method is allowed, if the cross-section can be
    classified as class 3 cross-section according to §10 (2).

    The reduced stress method does not consider load transfer between single
    plates.

    Args:
        rho: reduction factor :math:`\rho` from §10 (5), see calc_rho
        alpha_ultk: minimum load amplifier :math:`\alpha_{ult,k}` of the design
         loads, see calc_alpha_ultk
        stepper: Stepper object to which calculcation steps are added

    Returns:
        bool: True if permitted, Otherwise False

    """
    eta: float = rho * alpha_ultk / gamma_M1()
    valid: bool = eta > 1.0

    valid_str: str = 'valid' if valid else 'not valid'
    stepper.step(f"Reduced stress method is {valid_str} for "
                 f"\\rho = {rho}, \\alpha_{{ult,k}} = {alpha_ultk},"
                 f" \\gamma_{{M1}} = {gamma_M1()}.")
    return valid


def calc_bar_lambda_p(alpha_ultk: float,
                      alpha_cr: float) -> float:
    r"""Calculate the plate slenderness :math:`\bar{\lambda}_p`
    of the plate buckling field according to EN 1993-1-5:2019-10 §10 (3)

   Args:
       alpha_ultk: minimum load amplifier of the design loads to reach
        the characteristic resistance of the most critical cross-section,
        see calc_alpha_ultk
       alpha_cr: critical load factor for plate buckling
        (minimum force amplifier), see calc_alpha_cr

    Returns:
        FloatSequence: The plate slenderness :math:`\bar{\lambda}_p``.

    """
    bar_lambda_p: float = np.sqrt(alpha_ultk / alpha_cr)
    return bar_lambda_p


def calc_alpha_ultk(f_y: Pascal,
                    sigma_x_Ed: Pascal,
                    sigma_z_Ed: Pascal,
                    tau_Ed: Pascal) -> float:
    r"""Calculate :math:`\alpha_{ult,k}` for plate buckling

    :math:`\alpha_{ult,k}` is the minimum load amplifier of the design loads to
     reach the characteristic resistance of the most critical cross-section
    Calculations according to EN 1993-1-5:2019 §10 (4).

    Args:
        f_y: yield strength :math:`f_y`
        sigma_x_Ed: design value :math:`\sigma_{x,Ed}` of the longitudinal stress
        sigma_z_Ed: design value :math:`\sigma_{z,Ed}` of the transverse stress
        tau_Ed: design value :math:`\tau_{Ed}` of the shear stress

    Returns:
        float: :math:`\alpha_{ult,k}`: minimum load amplifier of the
         design loads
    """
    psi_x_Ed: float = sigma_x_Ed / f_y
    psi_z_Ed: float = sigma_z_Ed / f_y
    psi_tau_Ed: float = tau_Ed / f_y

    inv_alpha_ultk_sq: float = (psi_x_Ed ** 2
                                + psi_z_Ed ** 2
                                - psi_x_Ed * psi_z_Ed
                                + 3 * psi_tau_Ed ** 2)
    alpha_ultk: float = 1.0 / np.sqrt(inv_alpha_ultk_sq)
    return alpha_ultk


def calc_alpha_cr(alpha_crx: float, alpha_crz: float, alpha_crtau: float,
                  psi_x: float, psi_z: float) -> float:
    r"""Calculates :math:`\alpha_{cr}` from
    :math:`\sigma_{x,Ed}, \sigma_{z,Ed}, \tau_{Ed}`

    Necessary if no single :math:`\alpha_cr`` for the complete stress field,
     but :math:`\alpha_{cr,x}, \alpha_{cr,z}, \alpha_{cr,\tau}` are given.

    Calculations according to EN 1993-1-5:2019-10 §10 (6)

    Args:
        alpha_crx: :math:`\alpha_{cr,x}=\frac{\sigma_{cr,x}}{\sigma_{x,Ed}}`
        alpha_crz: :math:`\alpha_{cr,z}=\frac{\sigma_{cr,z}}{\sigma_{z,Ed}}`
        alpha_crtau: :math:`\alpha_{cr,\tau}=\frac{\\tau_{cr}}{\tau_{Ed}}`
        psi_x: Ratio :math:`\psi_x` of maximum vs minimum applied stress in
        x-direction
        psi_z: Ratio :math:`\psi_z` of maximum vs minimum applied stress in
        z-direction

    Returns:
        float: critical load factor :math:`\alpha_{cr}` for plate buckling
    """
    inv_alpha_cr: float = ((1 + psi_x) / (4 * alpha_crx)
                           + (1 + psi_z) / (4 * alpha_crz)
                           + np.sqrt(((1 + psi_x) / (4 * alpha_crx)
                                     + (1 + psi_z) / (4 * alpha_crz)) ** 2
                                     + (1 - psi_x) / (2 * alpha_crx ** 2)
                                     + (1 - psi_z) / (2 * alpha_crz ** 2)
                                     + 1.0 / (alpha_crtau ** 2)))
    alpha_cr: float = 1.0 / inv_alpha_cr
    return alpha_cr


def _calc_chi_w() -> NoReturn:
    r"""Calculate the reduction factor :math:`\chi_w` for shear buckling

    Calculation according to EN 1993-1-5:2019-10 §5.3(1).
    """
    raise NotImplementedError


ReductionMethod = Literal['smallest', 'interpolate']

def _calc_rho(support: PlateSupport,
             bar_lambda_p: float,
             psi: float = 1.0) -> float:
    r"""Calculates the reduction factor :math:`\\rho`

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

def calc_rho(method: ReductionMethod,
             support: PlateSupport,
             bar_lambda_p: float,
             psi_x: float,
             psi_z: float) -> FloatTriple:
    r"""Calculate reduction factors for the reduced stress method

    Returns the reduction factors :math:`\rho_x, \rho_z, \chi_w` for
     plate buckling in x-direction, z-direction and shear buckling respectively

    :math:`\chi_w` is currently not supported and set to 1.0

    Calculation according to EN 1993-1-5:2019-10 §10 (5)

    Args:
        method: 'smallest' or 'interpolated'
        support: PlateSupport.ONE_SIDE or PlateSupport.TWO_SIDE
        bar_lambda_p: plate slenderness :math:`\bar{\lambda}_p``
        psi_x: stress ratio :math:`\psi_x` in x-direction
        psi_z: stress ratio :math:`\psi_z` in z-direction

    Returns:
        FloatTriple:  :math:`\rho_x, \rho_z, \chi_w`

    """
    rho_x: float = _calc_rho(support, bar_lambda_p, psi_x)
    # Note for rho_z, §6 is neglected, instead 4.5.4(1) is used
    rho_z: float = _calc_rho(support, bar_lambda_p, psi_z)
    # chi_w: float = _calc_chi_w() # Currently not supported
    chi_w: float = 1.0

    if method == 'interpolate':
        return rho_x, rho_z, chi_w
    if method == 'smallest':
        min = np.min([rho_x, rho_z, chi_w])
        return (min,) * 3
    raise ValueError(f'Method {method} not supported.')


def calc_eta(f_y: Pascal,
             sigma_x_Ed: Pascal,
             sigma_z_Ed: Pascal,
             tau_Ed: Pascal,
             rho_x: float,
             rho_z: float,
             chi_w: float) -> Eta:
    r"""Calculates the load factor :math:`\eta`

    Calculates the load factor for plate buckling with the reduced stress
    method according to EN 1995-1-5:2019-10 §10 (5)

    Args:
        f_y: yield strength :math:`f_y`
        sigma_x_Ed: design value :math:`\sigma_{x,Ed}` of the
        longitudinal stress
        sigma_z_Ed: design value :math:`\sigma_{z,Ed}` of the
        transverse stress
        tau_Ed: design value :math:`\tau_{Ed}` of the shear stress
        rho_x: reduction factor :math:`\rho_x` for plate buckling in
         x-direction
        rho_z: reduction factor :math:`\rho_z` for plate buckling in
         y-direction
        chi_w: reduction factor :math:`\chi_w` for shear buckling

    Returns:
        Eta: load factor :math:`\eta`

    """
    # Interaction is already contained in this equation,
    # for this reason section 7 is not applied (see §10 (5)c) )
    V: float = rho_x * rho_z if (sigma_x_Ed > 0.0*Pascal() and
                                 sigma_z_Ed > 0.0*Pascal()) else 1.0
    f_yd: Pascal = f_y / gamma_M1()
    alpha_x: float = sigma_x_Ed / (rho_x * f_yd)
    alpha_z: float = sigma_z_Ed / (rho_z * f_yd)
    alpha_tau: float = tau_Ed / (chi_w * f_yd)
    eta_1: float = (alpha_x ** 2
                    + alpha_z ** 2
                    - V * alpha_x * alpha_z
                    + 3 * (alpha_tau ** 2))
    return eta_1
