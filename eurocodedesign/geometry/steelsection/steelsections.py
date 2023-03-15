""" 
classes for steel profiles
"""
from eurocodedesign.geometry.section import BasicSection
from abc import abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SteelSection(BasicSection):
    # add functionality if required later
    
    # ??? possible funcitonality could include calculation of axial, shear, and
    # ??? bending moment strengths -- with a steel material class as input
    pass

@dataclass(frozen=True)
class RolledISection(SteelSection):
    height: float
    flange_width: float
    web_thickeness: float
    flange_thickness: float
    root_radius: float
    weight: float
    perimeter: float
    area: float
    shear_area_z: float
    shear_area_y: float
    second_moment_of_area_y: float
    radius_of_gyration_y: float
    elastic_section_modulus_y: float
    plastic_section_modulus_y: float
    second_moment_of_area_z: float
    radius_of_gyration_z: float
    elastic_section_modulus_z: float
    plastic_section_modulus_z: float
    torsion_constant: float
    torsion_modulus: float
    warping_constant: float
    warping_modulus: float

    def print_properties(self) -> None:
        # TODO: implement a nice way of printing the properties
        raise NotImplementedError("IProfile.print_propteries() is not yet implemented")
