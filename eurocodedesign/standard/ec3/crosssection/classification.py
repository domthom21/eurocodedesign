""" Module for classifying steel cross-sections following EN 1993-1-1:2005 §5.5

# !!! only implemented for bending around the major (y-y axis)
# !!! only implemented for rolled doubly symmetric I-Sections, CHS, and Angles

# todo - check out exceptions in §6.2.1(10) and §6.2.2.4(1)
# todo - different epsilon value for QK4 using sigma_com (§5.5.2(9)/(10))
# todo - QK3 web and QK1/2 flanges - effective web following §6.2.2.4
# todo - implement for SHS/RHS, Welded I-Sections (sym. and asym.)
# todo - add examples

"""
from math import sqrt
from typing import Dict, List

from eurocodedesign.constants import mm, mm2, mm3, MPa
from eurocodedesign.core.typing import Pascal, Meter, Newton, Newtonmeter, \
    Meter_2, Meter_3
from eurocodedesign.geometry.steelsections import (
    RolledISection,
)
from eurocodedesign.materials.structuralsteel import BasicStructuralSteel


def calc_epsilon(f_yk: Pascal) -> float:
    """Calculates the material specific epsilon factor

    Args:
        f_yk (Pascal): The f_y value (yield stress) of the material
    Returns:
        float: the epsilon value according to EN 1993-1-1:2012-12 Tab.5.2
    """
    if not isinstance(f_yk, Pascal):
        raise TypeError("'f_yk' must be of type 'Pascal'.")
    return sqrt(235*MPa / f_yk)


def calc_k_sigma(psi: float, comp_free_edge: bool = True) -> float:
    if comp_free_edge:
        return 0.57 - 0.21 * psi + 0.07 * psi ** 2

    if psi == 1:
        return 0.43
    if psi >= 0:
        return 0.578 / (psi + 0.34)

    return 1.7 - 5 * psi + 17.1 * psi ** 2


def classify_dsup_element(
    c: Meter, t: Meter, f_yk: Pascal, alpha: float = 1.0, psi: float = 1.0
) -> int:
    slenderness = c / t
    ct_limits = ct_limits_dsup_elements(f_yk, alpha, psi)
    for section_class, slenderness_limit in reversed(list(ct_limits.items())):
        if not slenderness <= slenderness_limit:
            return section_class + 1
    return 1


def ct_limits_dsup_elements(f_yk: Pascal, alpha: float, psi: float) -> Dict[
        int, float]:
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


def ct_limit_ssup_element_class_3_tension_free_edge(f_yk: Pascal,
                                                    psi: float) -> float:
    return 21 * calc_epsilon(f_yk) * sqrt(
        calc_k_sigma(psi, comp_free_edge=False))


def classify_angle_cross_section(h: Meter, b: Meter, t: Meter,
                                 f_yk: Pascal) -> int:
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
    ct_limits = {
        1: 50 * eps ** 2,
        2: 70 * eps ** 2,
        3: 90 * eps ** 2,
    }
    return ct_limits


def classify_rolled_i_section(
    section: RolledISection,
    material: BasicStructuralSteel,
    N_Ed: Newton | None = None,
    M_Ed_y: Newtonmeter | None = None,
    M_Ed_z: Newtonmeter | None = None,
) -> int:
    if isinstance(M_Ed_z, Newtonmeter):
        raise NotImplementedError(
            "Cross-section classification for"
            " minor axis bending is not supported"
        )

    ct_vals = calc_i_section_cts(
        section.h*mm,
        section.b*mm,
        section.r*mm,
        section.t_w*mm,
        section.t_f*mm,
    )  # "Meter" required because units are not yet implemented for sections.
    
    web_class = classify_i_section_web(
        section, material, ct_vals["web"][0], ct_vals["web"][1], N_Ed, M_Ed_y)
    flange_class = classify_ssup_element(ct_vals["flange"][0],
                                         ct_vals["flange"][1], material.f_yk)
    cross_section_class = max(flange_class, web_class)

    return cross_section_class


def classify_i_section_web(section: RolledISection,
                           material: BasicStructuralSteel,
                           c: Meter, t: Meter,
                           N_Ed: Newton | None = None,
                           M_Ed_y: Newtonmeter | None = None
                           ) -> int:
    
    if not isinstance(N_Ed, Newton) and not isinstance(M_Ed_y, Newtonmeter):
        alpha_web: float = 1.0
        psi_web: float = 1.0

    elif not isinstance(N_Ed, Newton) and isinstance(M_Ed_y, Newtonmeter):
        alpha_web = calc_alpha_i_section_web(
            c, t, material.f_yk, Newton(0)
        )
        psi_web = calc_psi_i_section_web(
            section.A*mm2,
            section.W_ely*mm3,
            Newton(0),
            M_Ed_y,
        )

    elif isinstance(N_Ed, Newton) and not isinstance(M_Ed_y, Newtonmeter):
        
        try:
            alpha_web = calc_alpha_i_section_web(c, t, material.f_yk, N_Ed)
        
        except ValueError as e:
            if not str(e) == "Tension demand larger than web capacity.":
                raise ValueError(e)
            return 1       # because web is in tension it is class 1

        psi_web = calc_psi_i_section_web(
            section.A*mm2, section.W_ely*mm3, N_Ed,
            Newtonmeter(0)
        )

    elif isinstance(N_Ed, Newton) and isinstance(M_Ed_y, Newtonmeter):

        try:
            alpha_web = calc_alpha_i_section_web(c, t, material.f_yk, N_Ed)
        
        except ValueError as e:
            if not str(e) == "Tension demand larger than web capacity.":
                raise ValueError(e)
            return 1       # because web is in tension it is class 1
        
        psi_web = calc_psi_i_section_web(
            section.A*mm2, section.W_ely*mm3, N_Ed,
            M_Ed_y
        )

    if psi_web > 1: # the web is completely in tension under elastic conditions
       return 1
    else:
        return classify_dsup_element(c, t, material.f_yk, alpha_web, psi_web)



def calc_i_section_cts(
    h: Meter,
    b: Meter,
    weld_or_radius: Meter,
    t_w: Meter,
    t_f: Meter,
) -> Dict[str, List[Meter]]:
    c_flange: Meter = (b - (
        2 * weld_or_radius + t_w)) / 2
    c_web: Meter = h - 2 * (t_f + weld_or_radius)

    return {"flange": [c_flange, t_f], "web": [c_web, t_w]}


def calc_alpha_i_section_web(c: Meter, t: Meter, f_yk: Pascal,
                             N_Ed: Newton) -> float:
    e = abs(N_Ed) / (t * f_yk)
    if N_Ed < 0.0:
        alpha = 0.5 - e / (2 * c)
        if alpha <= 0.0:
            raise ValueError(
                "Tension demand larger than web capacity.")
    else:
        alpha = min(0.5 + e / (2 * c), 1.0)

    return alpha


def calc_psi_i_section_web(
    A: Meter_2, W_ely: Meter_3, N_Ed: Newton, M_Ed_y: Newtonmeter
) -> float:
    if N_Ed == 0 and M_Ed_y == 0:
        return 1.0  # testing for compression case if not loads are given

    # to_numeric avoids error when dividing "joule" by "Meter_3"
    sigma_N: Pascal = N_Ed / A  # +ve is compression
    sigma_M: Pascal = abs(M_Ed_y) / W_ely
    # section is symmetric -> compression on top

    sigma_top = sigma_N + sigma_M
    sigma_bottom = sigma_N - sigma_M

    return sigma_bottom / sigma_top
