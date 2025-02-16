from typing import NoReturn

from eurocodedesign.core.NA import loadNDP
from eurocodedesign.standard.ec3.steel_bridges import BridgeType
from eurocodedesign.units import Meter, Newton, kN, m, Pascal

def gamma_M0(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M0}` for steel bridges

    Partial factor for resistance of cross-sections (whatever the class is).
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: :math:`\gamma_{M0}` for current country

    """
    gamma_M0: float = float(
        ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M0',
                            default='1.00',
                            country=country))
    return gamma_M0


def gamma_Ff(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{Ff}` for fatigue load on steel bridges

    Value according to EN 1993-2:2010-12 §9.3(1)

    Returns: :math:`\gamma_{Ff}` for current country for steel bridges

    """
    gamma_Ff: float = float(
        load_NDP(key='EN1993-2_9.3_1#gamma_Ff',
                            default='1.0',
                            country=country))
    return gamma_Ff


def gamma_Mf(country: NACountry = NACountry.NONE) -> NoReturn:
    r"""
    Partial factor :math:`\gamma_{Mf}` for fatigue resistivity on steel bridges

    Value according to EN 1993-2:2010-12 §9.3(2), which references
    EN 1993-2 Tab. 3.1

    Returns: :math:`\gamma_{Mf}` for current country for steel bridges

    """
    raise NotImplementedError("Value from EN 1993-1-9:2010-12 Tab. 3.1"
                              " not implemented, yet.")


def calc_lambda_1(bridge_type: BridgeType,
                  L: Meter) -> float:
    r"""Calculate damage effect factor :math:`\lambda_1` of traffic

    Depends on the length of the critical influence line or area

    Args:
        L: Kritische Länge der Einflusslinie

    Returns:

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError

    if L < 10*m() or L > 80*m():
        raise ValueError(f"Span length {L} outside allowed range "
                         f"10 m <= L <= 80 m")
    # Feldbereich
        lambda_1 = 2.55 - 0.7 * (L-10*m())/(70*m())
    # Sützbereich
    if L >= 10*m() and L < 30*m():
        lambda_1 = 2.00 - 0.3 * (L-10*m())/(20*m())
    else:
        lambda_1 = 1.70 + 0.5 * (L-30*m())/(50*m())
    # TODO type midspan or support
    return lambda_1


def calc_lambda_2(bridge_type: BridgeType,
                  Q_m1: Newton,
                  N_Obs: int) -> float:
    r"""Calculate traffic volume factor :math:`\lambda_2`

    Args:
        bridge_type:
        Q_m1:
        N_Obs:

    Returns:

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    Q_0 = 480 * kN()
    N_0 = 0.5e6
    lambda_2 = Q_m1/Q_0*(N_Obs/N_0)**(1/5)
    return lambda_2


def calc_lambda_3(bridge_type: BridgeType, t_Ld: float) -> float:
    r"""Calculate bridge design life factor :math:`\lambda_3`

    Args:
        bridge_type:
        t_Ld: Nutzungsdauer in years as float

    Returns:

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    lambda_3 = (t_Ld/100)**(1/5)
    return 0.0


def calc_lambda_4(bridge_type: BridgeType) -> float:
    r"""Calculate traffic on other lanes factor :math:`\lambda_4`

    Args:
        bridge_type:

    Returns:

    """
    # only implemented if NA is used
    raise NotImplementedError


def calc_lambda_max(bridge_type: BridgeType, L: Meter) -> float:
    r"""Calculate maximum damage equivalence factor :math:`\lambda_{max}`

    According to 1993-2:2010-12 §9.5.2(7)

    Only span lengths between 10 and 80 meters are allowed.

    Args:
        bridge_type:

    Returns:

    """
    if bridge_type == BridgeType.RailwayBridge:
        lambda_max = 1.4
        return lambda_max
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    if L < 10*m() or L > 80*m():
        raise ValueError(f"Span length {L} outside allowed range "
                         f"{10*m()} <= L <= {80*m()}")
    # Feldbereich
    lambda_max = 2.00
    if L < 25*m() and L >= 10*m():
        lambda_max = 2.50 - 0.5 * (L-10*m())/(15*m())
    # Sützbereich
    lambda_Max = 1.80
    if L > 30*m() and L <= 80*m():
        lambda_max = 1.80 + 0.9 * (L-30*m())/(50*m())
    return lambda_max


def calc_lambda(lambda_1: float,
                lambda_2: float,
                lambda_3: float,
                lambda_4: float,
                lambda_max: float) -> float:
    r"""Calculate the fatigue equivalence factor :math:`lambda`

    Args:
        lambda_1:
        lambda_2:
        lambda_3:
        lambda_4:
        lambda_max:

    Returns:

    """
    lambda_ = lambda_1 * lambda_2 * lambda_3 * lambda_4
    lambda_ = lambda_ if lambda_ < lambda_max else lambda_max
    return lambda_


def get_Phi_2(bridge_type: BridgeType) -> float:
    r"""Get the damage equivalent impact factor :math:`\Phi_2`

    According to EN 1993-2:2010-12 §9.4.1(5)

    Returns 1.0 for road bridges and raises an NotImplementedError for
    railway bridges. For railway bridges :math:`\Phi_2` should be taken from
    EN 1991-2.

    Args:
        bridge_type: bridge type

    Returns: :math:`\Phi_2`

    """
    if bridge_type is BridgeType.RoadBridge:
        return 1.0
    raise NotImplementedError(f"Not implemented for {bridge_type}")


def calc_Delta_sigma_E2(lambda_: float,
                        Phi_2: float,
                        Delta_sigma_p: Pascal):
    # calculate damage equivalent stress range
    # related to 2x106 stess ranges
    Delta_sigma_E2 = lambda_ * Phi_2 * Delta_sigma_p
    return Delta_sigma_E2
