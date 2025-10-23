from typing import NoReturn

from eurocodedesign.core.NA import loadNDP, NACountry
from eurocodedesign.standard.ec3.steel_bridges import BridgeType, BridgeSection
from eurocodedesign.units import Meter, Newton, kN, m, Pascal


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


def lambda_1(bridge_type: BridgeType,
                  L: Meter,
                  bridge_section: BridgeSection) -> float:
    r"""Calculate damage effect factor :math:`\lambda_1` of traffic

    Depends on the length of the critical influence line or area

    According to EN 1993-2:2010-12 §9.5.2(2)

    The critical length parameter L has to be taken according to the standard
    depending on the structural context

    Args:
        L: critical length of the influence line

    Returns:
        damage effect factor :math:`\lambda_1` of traffic

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError

    if L < 10*m() or L > 80*m():
        raise ValueError(f"Span length {L} outside allowed range "
                         f"10 m <= L <= 80 m")
    if bridge_section == BridgeSection.Midspan:
        lambda_1 = 2.55 - 0.7 * (L-10*m())/(70*m())
    elif bridge_section == BridgeSection.Support:
        if L >= 10*m() and L < 30*m():
            lambda_1 = 2.00 - 0.3 * (L-10*m())/(20*m())
        else:
            lambda_1 = 1.70 + 0.5 * (L-30*m())/(50*m())
    else:
        raise ValueError(f"Invalid argument for parameter bridge_section: "
                         f"{bridge_section}")
    return lambda_1


def lambda_2(bridge_type: BridgeType,
                  Q_m1: Newton,
                  N_Obs: int) -> float:
    r"""Calculate traffic volume factor :math:`\lambda_2`

    According to EN 1993-2:2010-12 §9.5.2(3)

    Currently only implemented for road bridges

    Args:
        bridge_type: Bridge type
        Q_m1: average gross weight of lorries in the slow lane
        N_Obs: total number of lorries per year in the slow lane

    Returns:
        traffic volume factor :math:`\lambda_2`

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    Q_0 = 480 * kN()
    N_0 = 0.5e6
    lambda_2 = (Q_m1/Q_0)*(N_Obs/N_0)**(1/5)
    return lambda_2


def lambda_3(bridge_type: BridgeType, t_Ld: float) -> float:
    r"""Calculate bridge design life factor :math:`\lambda_3`

    According to EN 1993-2:2010-12 §9.5.2(3)

    Currently only implemented for road bridges

    Args:
        bridge_type: bridge type
        t_Ld: design life of the bridge in years as float

    Returns:
        bridge design life factor :math:`\lambda_3`

    """
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    lambda_3 = (t_Ld/100)**(1/5)
    return lambda_3


@NDP
def lambda_4(bridge_type: BridgeType,
                  k: float,
                  country: NACountry = '') -> float:
    r"""Calculate traffic on other lanes factor :math:`\lambda_4`

    According to EN 1993-2:2010-12 §9.5.2(4)

    Args:
        bridge_type: bridge typ
        k: number of lanes with heavy traffic

    Returns:
        traffic on other lanes factor :math:`\lambda_4`

    """
    # only implemented if NA is used
    if country == NACountry.DE:
        lambda_4 = (1+(k-1)*0.1)**(1/5)
        return lambda_4
    raise NotImplementedError


def lambda_max(bridge_type: BridgeType,
                    L: Meter,
                    bridge_section: BridgeSection) -> float:
    r"""Calculate maximum damage equivalence factor :math:`\lambda_{max}`

    According to 1993-2:2010-12 §9.5.2(7)

    Only railway bridges or
     road bridges with span lengths between 10 and 80 meters are allowed.

    Args:
        bridge_type: bridge type

    Returns:
        Maximum damage equivalence factor :math:`\lambda_{max}`

    """
    if bridge_type == BridgeType.RailwayBridge:
        lambda_max = 1.4
        return lambda_max
    if bridge_type != BridgeType.RoadBridge:
        raise NotImplementedError
    if L < 10*m() or L > 80*m():
        raise ValueError(f"Span length {L} outside allowed range "
                         f"{10*m()} <= L <= {80*m()}")
    if bridge_section == BridgeSection.Midspan:
        lambda_max = 2.00
        if L < 25*m() and L >= 10*m():
            lambda_max = 2.50 - 0.5 * (L-10*m())/(15*m())
    elif bridge_section == BridgeSection.Support:
        lambda_max = 1.80
        if L > 30*m() and L <= 80*m():
            lambda_max = 1.80 + 0.9 * (L-30*m())/(50*m())
    return lambda_max


def lambda(lambda_1: float,
                lambda_2: float,
                lambda_3: float,
                lambda_4: float,
                lambda_max: float) -> float:
    r"""Calculate the fatigue equivalence factor :math:`lambda`

    Args:
        lambda_1: factor for the damage effect of traffic
        lambda_2: factor for the traffic volumne
        lambda_3: factor for the design life of the bridge
        lambda_4: factor for the traffic on other lanes
        lambda_max: maximum lambda-value taking account of the fatigue limit

    Returns:
        fatigue equivalence factor :math:`lambda`

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

    Returns:
        damage equivalent impact factor :math:`\Phi_2`

    """
    if bridge_type is BridgeType.RoadBridge:
        return 1.0
    raise NotImplementedError(f"Not implemented for {bridge_type}")


def Delta_sigma_E2(lambda_: float,
                        Phi_2: float,
                        Delta_sigma_p: Pascal) -> Pascal:
    """
    Calculate the damage equivalent stress range related to 2x10e6 cycles

    According to EN 1993-2 §9.4(4)

    Delta_sigma_p is defined as the difference between maximum and minimum
    stress in influence areas
    :math:`\Delta\sigma_p=|\sigma_{p_max}-\sigma_{p_min}|`

    Args:
        lambda_: damage equivalence factor :math:`\lambda`
        Phi_2: damage equivalent impact factor :math:`\Phi_2`
        Delta_sigma_p: reference stress range :math:`\Delta\sigma_p`

    Returns:
        Delta_sigma_E2: Damage equivalent stress range :math:`\Delta\sigma_p`

    """
    Delta_sigma_E2 = lambda_ * Phi_2 * Delta_sigma_p
    return Delta_sigma_E2


def verify(gamma_Ff: float,
           Delta_sigma_E2: Pascal,
           gamma_Mf: float,
           Delta_sigma_c: Pascal) -> bool:
    """
    Verify if equivalent stress range is lower or equal than fatigue strength

    According to EN 1993-2:2012-12 §9.5.1

    Args:
        gamma_Ff: partial factor for fatigue loads
        Delta_sigma_E2: equivalent stress range
        gamma_Mf: partial factor for fatigue resistance
        Delta_sigma_c: fatigue strength

    Returns:
        True if valid

    """
    return gamma_Ff * Delta_sigma_E2 <= Delta_sigma_c / gamma_Mf
