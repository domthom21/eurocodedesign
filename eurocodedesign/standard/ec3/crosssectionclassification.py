""" Module for classifying steel cross-sections following EN 1993-1-1:2005 §5.5

# !!! only implemented for bending around the major (y-y axis)
# !!! only implemented for rolled doubly symmetric I-Sections, CHS, and Angles

# todo - check out exceptions in §6.2.1(10) and §6.2.2.4(1)
# todo - different epsilon value for QK4 using sigma_com (§5.5.2(9)/(10))
# todo - QK3 web and QK1/2 flanges - effective web following §6.2.2.4
# todo - implement for SHS/RHS, Welded I-Sections (sym. and asym.)

"""
from math import sqrt
from typing import Tuple, Callable, cast, Dict, List
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
    Meter_4,
    mm,
    mm2,
    mm3,
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

    # if alpha != 1.0 and psi == 1.0:
    #     raise ValueError(
    #         "The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'."
    #     )

    # if alpha == 1.0 and psi != 1.0:
    #     raise ValueError(
    #         "The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'."
    #     )

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

    # if alpha != 1.0 and psi == 1.0:
    #     raise ValueError(
    #         "The default 'psi' value does not correspond to the user defined value for 'alpha'. Specify a value for 'psi'."
    #     )

    # if alpha == 1.0 and psi != 1.0:
    #     raise ValueError(
    #         "The default 'alpha' value does not correspond to the user defined value for 'psi'. Specify a value for 'alpha'."
    #     )

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
    ct_limits = {
        1: 50 * eps**2,
        2: 70 * eps**2,
        3: 90 * eps**2,
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
            "Cross-section classification for minor axis bending is not supported"
        )

    ct_vals = calc_i_section_cts(
        mm(section.height),
        mm(section.flange_width),
        mm(section.root_radius),
        mm(section.web_thickness),
        mm(section.flange_thickness),
    )  # "Meter" required because units are not yet implemented for the sections.

    if not isinstance(N_Ed, Newton) and not isinstance(M_Ed_y, Newtonmeter):
        alpha_web: float = 1.0
        psi_web: float = 1.0

    elif not isinstance(N_Ed, Newton) and isinstance(M_Ed_y, Newtonmeter):
        alpha_web = calc_alpha_i_section_web(
            ct_vals["web"][0], ct_vals["web"][1], material.f_yk, Newton(0)
        )
        psi_web = calc_psi_i_section_web(
            mm2(section.area),
            mm3(section.elastic_section_modulus_y),
            Newton(0),
            M_Ed_y,
        )

    elif isinstance(N_Ed, Newton) and not isinstance(M_Ed_y, Newtonmeter):
        alpha_web = calc_alpha_i_section_web(ct_vals["web"][0], ct_vals["web"][1], material.f_yk, N_Ed)
        psi_web = calc_psi_i_section_web(
            mm2(section.area), mm3(section.elastic_section_modulus_y), N_Ed, Newtonmeter(0)
            )
    
    elif isinstance(N_Ed, Newton) and isinstance(M_Ed_y, Newtonmeter):
        alpha_web = calc_alpha_i_section_web(ct_vals["web"][0], ct_vals["web"][1], material.f_yk, N_Ed)
        psi_web = calc_psi_i_section_web(
                mm2(section.area), mm3(section.elastic_section_modulus_y), N_Ed, M_Ed_y
                )
            

    web_class = classify_dsup_element(
        ct_vals["web"][0], ct_vals["web"][1], material.f_yk, alpha_web, psi_web
    )

    flange_class = classify_ssup_element(ct_vals["flange"][0], ct_vals["flange"][1], material.f_yk)
    cross_section_class = max(flange_class, web_class)

    return cross_section_class


def calc_i_section_cts(
    h: Meter,
    b: Meter,
    weld_or_radius: Meter,
    t_w: Meter,
    t_f: Meter,
) -> Dict[str, List[Meter]]:
    
    # .to_numeric required to avoid assignment errors from mypy and Unit Module
    c_flange = Meter(b.to_numeric() - (2 * weld_or_radius.to_numeric() + t_w.to_numeric()) / 2)
    c_web = Meter(h.to_numeric() - 2 * (t_f.to_numeric() + weld_or_radius.to_numeric()))

    return {"flange": [c_flange, t_f], "web": [c_web, t_w]}


def calc_alpha_i_section_web(c: Meter, t: Meter, f_yk: Pascal, N_Ed: Newton) -> float:
    e = abs(N_Ed.to_numeric()) / (t.to_numeric() * f_yk.to_numeric())
    if N_Ed.to_numeric() < 0.0:
        alpha = 0.5 - e / (2 * c.to_numeric())
        if alpha <= 0.0:
            raise NotImplementedError("Tension demand larger than web capacity.")
    else:
        alpha = min(0.5 + e / (2 * c.to_numeric()), 1.0)

    return alpha


def calc_psi_i_section_web(
    A: Meter_2, W_ely: Meter_3, N_Ed: Newton, M_Ed_y: Newtonmeter
) -> float:
    if N_Ed.to_numeric() == 0 and M_Ed_y.to_numeric() == 0:
        return 1.0  # testing for compression case if not loads are given

    # to_numeric avoids error when dividing "joule" by "Meter_3"
    sigma_N = Pascal(N_Ed.to_numeric() / A.to_numeric())  # +ve is compression
    sigma_M = Pascal(
        abs(M_Ed_y.to_numeric()) / W_ely.to_numeric()
    )  # section is symmetric -> compression on top

    sigma_top = sigma_N + sigma_M
    sigma_bottom = sigma_N - sigma_M

    return sigma_bottom / sigma_top
