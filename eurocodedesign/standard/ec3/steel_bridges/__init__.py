"""
Module for EN 1993-2 calculations. EN 1993-2 provides a basis for the structural
design of steel bridges and steel parts of composite bridges.
"""
from enum import Enum, unique, auto

import eurocodedesign as ed
from eurocodedesign.core.NA import NDP, NACountry


@unique
class BridgeType(Enum):
    RoadBridge = auto()
    RailwayBridge = auto()


@unique
class BridgeSection(Enum):
    Midspan = auto()
    Support = auto()


@NDP
def gamma_M0(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M0}` for steel bridges

    Partial factor for resistance of members and cross sections to
    excessive yielding including local buckling
    Value according to EN 1993-2:2010-12 §6.1(1) or NA

    Returns: :math:`\gamma_{M0}` for current country

    """
    gamma_M0: float = float(
        ed.core.NA.load_NDP(key='EN1993-2_6.1_note_2#gamma_M0',
                            default=str(ed.standard.ec3.gamma_M0),
                            country=country))
    return gamma_M0


@NDP
def gamma_M1(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M1}` for steel bridges

    Partial factor for resistance of members to instability assessed by
    member checks.
    Value according to EN 1993-2 §6.1(1) or NA

    Returns: :math:`\gamma_{M1}` for current country

    """
    gamma_M1: float = float(
        ed.core.NA.load_NDP(key='EN1993-2_6.1_note_2#gamma_M1',
                            default=str(ed.standard.ec3.gamma_M1),
                            country=country))
    return gamma_M1


@NDP
def gamma_M2(country: NACountry = NACountry.NONE) -> float:
    r"""
    Partial factor :math:`\gamma_{M2}` for steel bridges

    Partial factor for resistance of cross-sections in tension to fracture.
    Value according to EN 1993-2:2010-12 §6.1(1) or NA

    Returns: :math:`\gamma_{M2}` for current country

    """
    gamma_M2: float = float(
        ed.core.NA.load_NDP(key='EN1993-2_6.1_note_2#gamma_M2',
                            default=str(ed.standard.ec3.gamma_M2),
                            country=country))
    return gamma_M2
