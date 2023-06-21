""" Module for classifying steel cross-sections following Eurocode 3 §5.5


# todo - check out exceptions in §6.2.1(10) and §6.2.2.4(1)
# todo - different epsilon value for QK4 using sigma_com (§5.5.2(9)/(10))
# todo - QK3 web and QK1/2 flanges - effective web following §6.2.2.4


# !!! only implemented for bending around the major (y-y axis)
# !!! only implemented for rolled doubly symmetric I-Sections, CHS, RHS, SHS

"""
from math import sqrt
from typing import Tuple, Callable
import numpy as np
from eurocodedesign.geometry.steelsections import (
    SteelSection,
    ISection,
    RolledISection,
    CircularHollowSection,
    SquareHollowSection,
    RectangularHollowSection,
)
from eurocodedesign.materials.structuralsteel import BasicStructuralSteel
from eurocodedesign.units import Newton, Meter_2, Pascal


def _section_classification(
    section: SteelSection,
    material: BasicStructuralSteel,
    axial_force: float = 0,
    bending_moment: float = 0,
) -> int:
    # based on section type call the appropriate function to calculate class
    # todo
    if isinstance(section, CircularHollowSection):
        section_class = _chs_section_classification(section, material)

    elif (
        isinstance(section, RectangularHollowSection)
        or isinstance(section, SquareHollowSection)
        or isinstance(section, ISection)
    ):
        section_class = _rhs_shs_i_section_classification(
            section, material, axial_force, bending_moment
        )

    else:
        raise NotImplementedError(f"Section type currently not supported")

    return section_class


def _rhs_shs_i_section_classification(
    section: ISection | RectangularHollowSection | SquareHollowSection,
    material: BasicStructuralSteel,
    axial_force: float,
    bending_moment: float,
) -> int:
    (
        web_slenderness,
        flange_slenderness,
        weld_radius,
        limit_function,
    ) = _section_specific_classification_parameters(section)
    # flange_slenderness = _flange_slenderness(section)
    eps = get_epsilon(material)

    # try from least strict to most strict class until criteria not satisfied
    for section_class in [3, 2, 1]:
        if section_class == 3:
            distribution_parameter = _psi_for_major_axis_symmetric_sections(
                axial_force, bending_moment, section
            )
        else:
            distribution_parameter = _alpha_for_major_axis_symmetric_sections(
                section, material, axial_force, weld_radius
            )

        if not limit_function(
            web_slenderness,
            flange_slenderness,
            distribution_parameter,
            eps,
            section_class,
        ):
            return section_class + 1
    return 1


def _section_specific_classification_parameters(
    section: SteelSection,
) -> Tuple[float, float, float, Callable[..., bool]]:
    # returns the correct web slenderness depending on the section type
    # todo
    if isinstance(section, RolledISection):
        web_slenderness = _web_slenderness_for_I_section(section)
        flange_slenderness = _flange_slenderness_for_symmetric_I_section(section)
        weld_radius = section.root_radius
        slenderness_limit_func = i_section_web_and_flange_slenderness_lt_limit

    elif isinstance(section, RectangularHollowSection) or isinstance(
        section, SquareHollowSection
    ):
        web_slenderness = _web_slenderness_for_rhs_shs_sections(section)
        flange_slenderness = _flange_slenderness_for_rhs_shs_sections(section)
        weld_radius = section.outer_corner_radius
        slenderness_limit_func = shs_rhs_web_and_flange_slenderness_lt_limit

    return (
        web_slenderness,
        flange_slenderness,
        weld_radius,
        slenderness_limit_func,
    )


def shs_rhs_web_and_flange_slenderness_lt_limit(
    web_slenderness: float,
    flange_slenderness: float,
    distribution_parameter: float,
    epsilon: float,
    section_class: int,
) -> bool:
    # todo: refactor
    web_limit = _boundary_ct_for_double_supported_elements(
        distribution_parameter, epsilon, section_class
    )
    flange_limit = _boundary_ct_for_double_supported_elements(1, epsilon, section_class)
    if web_slenderness <= web_limit and flange_slenderness <= flange_limit:
        return True
    else:
        return False


def i_section_web_and_flange_slenderness_lt_limit(
    web_slenderness: float,
    flange_slenderness: float,
    distribution_parameter: float,
    epsilon: float,
    section_class: int,
) -> bool:
    # todo: refactor
    web_limit = _boundary_ct_for_double_supported_elements(
        distribution_parameter, epsilon, section_class
    )
    flange_limit = _boundary_ct_for_single_supported_elements(epsilon, section_class)
    if web_slenderness <= web_limit and flange_slenderness <= flange_limit:
        return True
    else:
        return False


def _chs_section_classification(
    section: CircularHollowSection, material: BasicStructuralSteel
) -> int:
    slenderness = _slenderness_for_chs_elements(section)
    eps = get_epsilon(material)
    for section_class in [3, 2, 1]:
        if not slenderness <= _boundary_ct_for_chs_elements(eps, section_class):
            return section_class + 1
    return 1


### GENERAL LIMITS AND STUFF
def _boundary_ct_for_double_supported_elements(
    distribution_parameter: float, epsilon: float, section_class: int
) -> float:
    """Returns the boundary value of c/t for doubly supported elements

    The boundary values are calculated using the equations provided in Table 5.2
    of Eurocode 3.

    Args:
        distribution_parameter (float): alpha or psi parameters depending on the
            choic of section_class
        epsilon (float): modification factor for steel different steel strengths
        section_class: the section class boundaries considered. One of 1, 2, 3

    Returns:
        float: the boundary value for c/t
    """
    alpha: float
    if section_class == 1:
        alpha = distribution_parameter
        if distribution_parameter > 0.5:
            return 396 * epsilon / (13 * alpha - 1)
        else:
            return 36 * epsilon / alpha

    elif section_class == 2:
        alpha = distribution_parameter
        if alpha > 0.5:
            return 456 * epsilon / (13 * alpha - 1)
        else:
            return 41.5 * epsilon / alpha

    elif section_class == 3:
        psi: float = distribution_parameter
        if psi > -1:
            return 42 * epsilon / (0.67 + 0.33 * psi)
        else:
            return 62 * epsilon * (1 - psi) * sqrt(-psi)

    else:
        raise ValueError(f"Invalid section class: '{section_class}'")


def _boundary_ct_for_single_supported_elements(
    epsilon: float, section_class: int
) -> float:
    # only considers the flange fully in compressionas this is worst case but
    # also the easiest to calculate
    if section_class == 1:
        return 9 * epsilon
    elif section_class == 2:
        return 10 * epsilon
    elif section_class == 3:
        return 14 * epsilon
    else:
        raise ValueError('Invalid cross-section class ', section_class)


def normal_stress(normal_force: Newton, area: Meter_2) -> Pascal:
    return Pascal(normal_force / area)


def bending_stress(bending_moment: float, section_modulus: float) -> Pascal: # todo fix float types
    return Pascal(bending_moment / section_modulus)


def get_epsilon(material: BasicStructuralSteel) -> float:
    return sqrt(235 / material.f_yk) # todo fix types


def _e_from_normal_force(
    section: ISection | SquareHollowSection | RectangularHollowSection,
    material: BasicStructuralSteel,
    axial_force: Newton,
    gamma_M0: float = 1.0,
) -> Pascal:
    """Calculates the length of the web required to carry the axial force

    The web is assumed to be completely plastified. The axial load is assumed
    to be completely carried by the web.

    Args:
        section (ISection|SquareHollowSection|RectangularHollowSection):
            section to analyse
        material (BasicStructuralSteel): steel material of the cross-section
        axial_force (float): axial acting on the section
        gamma_M0 (float): partial safety factor for steel materials.
            Default: 1.0

    Returns:
        float: length of web required to carry the axial force
    """
    if isinstance(section, ISection):
        return axial_force * gamma_M0 / (material.f_yk * section.web_thickness) # todo fix f_yk type
    elif (isinstance(section, SquareHollowSection) or
          isinstance(section, RectangularHollowSection)):
        return axial_force * gamma_M0 / (material.f_yk * 2 * section.wall_thickness)
    else:
        raise NotImplementedError(
            f"Section Classification for {section.name} is not yet implemented"
        )


def _psi_for_major_axis_symmetric_sections(
    axial_force: float,
    bending_moment: float,
    section: ISection | SquareHollowSection | RectangularHollowSection,
) -> float:
    # compression is +, positive moment is tension on bottom
    stress_N = normal_stress(axial_force, section.area)
    stress_M = bending_stress(bending_moment, section.elastic_section_modulus_y)
    top_stress = stress_N + stress_M
    bottom_stress = stress_N - stress_M
    return bottom_stress / top_stress


def _alpha_for_major_axis_symmetric_sections(
    section: ISection | RectangularHollowSection | SquareHollowSection,
    material: BasicStructuralSteel,
    axial_force: float,
    weld_or_radius: float,
) -> float:
    """calculates the alpha value for sections symmetric about their major axis

    alpha is the fraction of the total clear length of the web(s) that is loaded
    in compression considering the given axial force and the corresponding
    maximum moment capacity of the cross-section (fully plastic)

    Args:
        section (ISection | RectangularHollowSection | SquareHollowSection):
            section to analyse
        material (BasicStructuralSteel): steel material of the cross-section
        axial_force (float): axial force acting on cross-section
        weld_or_radius (float): weld thickness or radius between flange and web

    Returns:
        float: the value of alpha
    """
    if isinstance(section, ISection):
        c = _c_web_for_symmetric_I_section(section, weld_or_radius)
    elif isinstance(section, RectangularHollowSection) or isinstance(
        section, SquareHollowSection
    ):
        c = _c_web_for_rhs_shs_sections(section)
    e = _e_from_normal_force(section, material, axial_force, gamma_M0=1)
    alpha = min(1.0, (c / 2 + e / 2) / c)  # required when N gt capacitiy of web

    return alpha


### ISECTION SPECIFIC STUFF
def _web_slenderness_for_I_section(section: ISection) -> float:
    """returns the the slenderness (c/t) value of the web of the I section"""
    if isinstance(section, RolledISection):
        return (
            _c_web_for_symmetric_I_section(section, section.root_radius)
            / section.web_thickness
        )
    else:
        raise NotImplementedError(f"section: {section.name} not yet supported")


def _flange_slenderness_for_symmetric_I_section(section: ISection) -> float:
    """returns the the slenderness (c/t) value of the flange of the I section"""
    if isinstance(section, RolledISection):
        return (
            _c_flange_for_symmetric_I_section(section, section.root_radius)
            / section.flange_thickness
        )
    else:
        raise NotImplementedError(f"section: {section.name} not yet supported")


def _c_web_for_symmetric_I_section(section: ISection, weld_or_radius: float) -> float:
    """calculates the clear length of web between welds or radii, c_web"""
    return section.height - 2 * (section.flange_thickness + weld_or_radius)


def _c_flange_for_symmetric_I_section(
    section: ISection, weld_or_radius: float
) -> float:
    """calculates the clear length of flange from the edge of the radius or weld"""
    return (section.flange_width - 2 * weld_or_radius - section.web_thickness) / 2


### CHS Specific Stuff
def _boundary_ct_for_chs_elements(epsilon: float, section_class: int) -> float:
    if section_class == 1:
        return 50 * epsilon**2
    elif section_class == 2:
        return 70 * epsilon**2
    elif section_class == 3:
        return 90 * epsilon**2


def _slenderness_for_chs_elements(section: CircularHollowSection) -> float:
    """returns the the slenderness (d/t) value of the CHS section"""
    return section.diameter / section.wall_thickness


### SHS/RHS Specific Stuff
def _c_web_for_rhs_shs_sections(
    section: RectangularHollowSection | SquareHollowSection,
) -> float:
    """Returns the clear distance of the web between the corner radii"""
    return section.height - 2 * section.outer_corner_radius


def _c_flange_for_rhs_shs_sections(
    section: RectangularHollowSection | SquareHollowSection,
) -> float:
    """Returns the clear distance of the flange between the corner radii"""
    return section.width - 2 * section.outer_corner_radius


def _web_slenderness_for_rhs_shs_sections(
    section: RectangularHollowSection | SquareHollowSection,
) -> float:
    """returns the the slenderness (c/t) value of web the SHS/RHS section"""
    return _c_web_for_rhs_shs_sections(section) / section.wall_thickness


def _flange_slenderness_for_rhs_shs_sections(
    section: RectangularHollowSection | SquareHollowSection,
) -> float:
    """returns the the slenderness (c/t) value of flange the SHS/RHS section"""
    return _c_flange_for_rhs_shs_sections(section) / section.wall_thickness


if __name__ == "__main__":
    import eurocodedesign.geometry.steelsections as sec
    import eurocodedesign.materials.structuralsteel as stl

    # section_class = _rhs_shs_section_classification(
    #     sec.get("SHS140x4"), stl.S355(), 500_000, 0.0
    # )
    # print(section_class)
