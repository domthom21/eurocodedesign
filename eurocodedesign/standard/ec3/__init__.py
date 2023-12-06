import eurocodedesign as ed
from eurocodedesign.core.NA import NDP, NACountry


@NDP
def gamma_M0(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M0}` for buildings

    Partial factor for resistance of cross-sections (whatever the class is).
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: :math:`\gamma_{M0}` for current country

    """
    gamma_M0: float = float(
        ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M0',
                            default='1.00',
                            country=country))
    return gamma_M0


@NDP
def gamma_M1(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M1}` for buildings

    Partial factor for resistance of members to instability assessed by
    member checks.
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: :math:`\gamma_{M1}` for current country

    """
    gamma_M1: float = float(
        ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M1',
                            default='1.00',
                            country=country))
    return gamma_M1


@NDP
def gamma_M2(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M2}` for buildings

    Partial factor for resistance of cross-sections in tension to fracture.
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: :math:`\gamma_{M2}` for current country

    """
    gamma_M2: float = float(
        ed.core.NA.load_NDP(key='EN1993-1-1_6.1_note_2b#gamma_M2',
                            default='1.25',
                            country=country))
    return gamma_M2
