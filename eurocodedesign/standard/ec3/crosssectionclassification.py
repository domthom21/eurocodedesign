""" Module for classifying steel cross-sections following EN 1993-1-1:2005 §5.5


# todo - check out exceptions in §6.2.1(10) and §6.2.2.4(1)
# todo - different epsilon value for QK4 using sigma_com (§5.5.2(9)/(10))
# todo - QK3 web and QK1/2 flanges - effective web following §6.2.2.4


# !!! only implemented for bending around the major (y-y axis)
# !!! only implemented for rolled doubly symmetric I-Sections, CHS, RHS, SHS

"""
from math import sqrt
from typing import Tuple, Callable, cast, Dict
from eurocodedesign.geometry.steelsections import (
    SteelSection,
    ISection,
    RolledISection,
    CircularHollowSection,
    SquareHollowSection,
    RectangularHollowSection,
)
from eurocodedesign.materials.structuralsteel import BasicStructuralSteel
from eurocodedesign.units import (
    Newton,
    Meter_2,
    Pascal,
    MPa,
    N,
    mm,
    N_per_mm2,
    Meter,
    Newtonmeter,
    Meter_3,
)


def calc_epsilon(f_yk: Pascal) -> float:
    """Calculates the material specific epsilon factor

    Args:
        f_yk (Pascal): The f_y value (yield stress) of the material
    Returns:
        float: the epsilon value according to EN 1993-1-1:2012-12 Tab.5.2
    """
    if not isinstance(f_yk, Pascal):
        raise TypeError("'f_yk' must be of type 'Pascal'.")
    return sqrt(235 * MPa() / f_yk)


def calc_k_sigma(psi: float, comp_free_edge: bool = True) -> float:
    if comp_free_edge:
        return 0.57 - 0.21 * psi + 0.07 * psi**2

    if psi == 1:
        return 0.43
    if psi >= 0:
        return 0.578 / (psi + 0.34)

    return 1.7 - 5 * psi + 17.1 * psi**2


def classify_dsup_element(
    c: Meter, t: Meter, f_yk: Pascal, alpha: float = 1.0, psi: float = 1.0
) -> int:
    slenderness = c / t

    if alpha != 1.0 and psi == 1.0:
        raise ValueError(
            "The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'."
        )

    if alpha == 1.0 and psi != 1.0:
        raise ValueError(
            "The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'."
        )

    ct_limits = ct_limits_dsup_elements(f_yk, alpha, psi)

    for section_class, slenderness_limit in reversed(list(ct_limits.items())):
        if not slenderness <= slenderness_limit:
            return section_class + 1

    return 1


def ct_limits_dsup_elements(f_yk: Pascal, alpha: float, psi: float) -> Dict[int, float]:
    ct_limits = {
        1: ct_limit_dsup_element_class_1(f_yk, alpha),
        2: ct_limit_dsup_element_class_2(f_yk, alpha),
        3: ct_limit_dsup_element_class_3(f_yk, psi),
    }
    return ct_limits


def ct_limit_dsup_element_class_1(f_yk: Pascal, alpha: float) -> float:
    eps = calc_epsilon(f_yk)
    if alpha <= 0.5:
        return 36 * eps / alpha
    else:
        return 396 * eps / (13 * alpha - 1)


def ct_limit_dsup_element_class_2(f_yk: Pascal, alpha: float) -> float:
    eps = calc_epsilon(f_yk)
    if alpha <= 0.5:
        return 41.5 * eps / alpha
    else:
        return 456 * eps / (13 * alpha - 1)


def ct_limit_dsup_element_class_3(f_yk: Pascal, psi: float) -> float:
    eps = calc_epsilon(f_yk)
    if psi <= -1:
        return 62 * eps * (1 - psi) * sqrt(-psi)
    else:
        return 42 * eps / (0.67 + 0.33 * psi)


def classify_ssup_element(
    c: Meter,
    t: Meter,
    f_yk: Pascal,
    alpha: float = 1.0,
    psi: float = 1.0,
    comp_free_edge: bool = True,
) -> int:
    slenderness = c / t

    if alpha != 1.0 and psi == 1.0:
        raise ValueError(
            "The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'."
        )

    if alpha == 1.0 and psi != 1.0:
        raise ValueError(
            "The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'."
        )

    ct_limits = ct_limits_ssup_elements(f_yk, alpha, psi, comp_free_edge)

    for section_class, slenderness_limit in reversed(list(ct_limits.items())):
        if not slenderness <= slenderness_limit:
            return section_class + 1

    return 1


def ct_limits_ssup_elements(
    f_yk: Pascal, alpha: float, psi: float, comp_free_edge: bool = True
) -> Dict[int, float]:
    if comp_free_edge:
        ct_limits = {
            1: ct_limit_ssup_element_class_1(f_yk, alpha),
            2: ct_limit_ssup_element_class_2(f_yk, alpha),
            3: ct_limit_ssup_element_class_3(f_yk, psi),
        }
        return ct_limits

    ct_limits = {
        1: ct_limit_ssup_element_class_1_tension_free_edge(f_yk, alpha),
        2: ct_limit_ssup_element_class_2_tension_free_edge(f_yk, alpha),
        3: ct_limit_ssup_element_class_3_tension_free_edge(f_yk, psi),
    }
    return ct_limits


def ct_limit_ssup_element_class_1(f_yk: Pascal, alpha: float) -> float:
    return 9 * calc_epsilon(f_yk) / alpha


def ct_limit_ssup_element_class_1_tension_free_edge(
    f_yk: Pascal, alpha: float
) -> float:
    return 9 * calc_epsilon(f_yk) / (alpha * sqrt(alpha))


def ct_limit_ssup_element_class_2(f_yk: Pascal, alpha: float) -> float:
    return 10 * calc_epsilon(f_yk) / alpha


def ct_limit_ssup_element_class_2_tension_free_edge(
    f_yk: Pascal, alpha: float
) -> float:
    return 10 * calc_epsilon(f_yk) / (alpha * sqrt(alpha))


def ct_limit_ssup_element_class_3(f_yk: Pascal, psi: float) -> float:
    if psi == 1.0:
        return 14 * calc_epsilon(f_yk)

    return 21 * calc_epsilon(f_yk) * sqrt(calc_k_sigma(psi))


def ct_limit_ssup_element_class_3_tension_free_edge(f_yk: Pascal, psi: float) -> float:
    return 21 * calc_epsilon(f_yk) * sqrt(calc_k_sigma(psi, comp_free_edge=False))


def classify_angle_cross_section(h: Meter, b: Meter, t: Meter, f_yk: Pascal) -> int:
    slenderness = h / t
    slenderess_2 = (b + h) / (2 * t)
    eps = calc_epsilon(f_yk)
    
    limit_one = 15 * eps
    limit_two = 11.5 * eps
    
    if slenderness <= limit_one and slenderess_2 <= limit_two:
        return 3
        
    return 4


def classify_chs_cross_section(d: Meter, t: Meter, f_yk: Pascal) -> int:
    slenderness = d / t

    ct_limits = ct_limits_chs_elements(f_yk)

    for section_class, slenderness_limit in reversed(list(ct_limits.items())):
        if not slenderness <= slenderness_limit:
            return section_class + 1

    return 1
    

def ct_limits_chs_elements(f_yk: Pascal) -> Dict[int, float]:
    eps = calc_epsilon(f_yk)
    ct_limits = {1: 50 * eps**2,
                 2: 70 * eps**2,
                 3: 90 * eps**2,
                }
    return ct_limits