""" Material properties of structural steel

Classes defining the different types of construction steel that are permitted
within the Eurocode framework. The different steel types are defined by the
following standards:
    -- EN 10025-2
    -- EN 10025-3
    -- EN 10025-4
    -- EN 10025-5
    -- EN 10025-6
    -- EN 10210-1
    -- EN 10219-1

All material strengths are given in MPa (N/mm2) unless otherwise indicated

Example Usage:

    import eurocodedesign.materials.structuralsteel as ss
    # S235 steel material with thickness <= 40 mm
    steel_material = ss.get("S235", True)
    # S355 steel material with thickness >= 40 mm
    steel_material = ss.get("S355", False)

    yield_stress = steel_material.f_yk
    ultimate_stress = steel_material.f_uk

    elastic_modulus = steel_material.E
    shear_modulus = steel_material.G
    thermal_coefficient = steel_material.alpha
"""
from dataclasses import dataclass, field
from typing import Type

from eurocodedesign.units import Pascal, mm2, N


@dataclass(frozen=True)
class BasicStructuralSteel():
    thickness_le_40mm: bool = field(default=True)
    name: str = field(default="")
    _elastic_modulus: Pascal = field(
        default_factory=lambda: 210_000 * N() / mm2(), kw_only=True)
    _shear_modulus: Pascal = field(
        default_factory=lambda: 81_000 * N() / mm2(), kw_only=True)
    _thermal_coefficient: float = field(default=1.2e-7, kw_only=True)  # 1/K
    poissons_ratio: float = field(default=0.3, kw_only=True)

    f_y_thin: Pascal = field(default_factory=lambda: Pascal(0), kw_only=True)
    f_y_thick: Pascal = field(default_factory=lambda: Pascal(0), kw_only=True)
    f_u_thin: Pascal = field(default_factory=lambda: Pascal(0), kw_only=True)
    f_u_thick: Pascal = field(default_factory=lambda: Pascal(0), kw_only=True)

    @property
    def f_yk(self) -> Pascal:
        if self.thickness_le_40mm:
            return self.f_y_thin
        else:
            return self.f_y_thick

    @property
    def f_uk(self) -> Pascal:
        if not self.thickness_le_40mm:
            return self.f_u_thin
        else:
            return self.f_u_thick

    @property
    def E(self) -> Pascal:
        return self._elastic_modulus

    @property
    def G(self) -> Pascal:
        return self._shear_modulus

    @property
    def alpha(self) -> float:
        return self._thermal_coefficient


@dataclass(frozen=True, kw_only=True)
class S235(BasicStructuralSteel):
    name: str = "S235"
    f_y_thin: Pascal = field(default_factory=lambda: 235 * N() / mm2())
    f_u_thin: Pascal = field(default_factory=lambda: 360 * N() / mm2())
    f_y_thick: Pascal = field(default_factory=lambda: 215 * N() / mm2())
    f_u_thick: Pascal = field(default_factory=lambda: 360 * N() / mm2())
    norm: str = "EN 10025-2"


@dataclass(frozen=True, kw_only=True)
class S275(BasicStructuralSteel):
    name: str = "S275"
    f_y_thin: Pascal = field(default_factory=lambda: 275 * N() / mm2())
    f_u_thin: Pascal = field(default_factory=lambda: 430 * N() / mm2())
    f_y_thick: Pascal = field(default_factory=lambda: 255 * N() / mm2())
    f_u_thick: Pascal = field(default_factory=lambda: 410 * N() / mm2())
    norm: str = "EN 10025-2"


@dataclass(frozen=True, kw_only=True)
class S355(BasicStructuralSteel):
    name: str = "S355"
    f_y_thin: Pascal = field(default_factory=lambda: 355 * N() / mm2())
    f_u_thin: Pascal = field(default_factory=lambda: 490 * N() / mm2())
    f_y_thick: Pascal = field(default_factory=lambda: 335 * N() / mm2())
    f_u_thick: Pascal = field(default_factory=lambda: 470 * N() / mm2())
    norm: str = "EN 10025-2"


@dataclass(frozen=True, kw_only=True)
class S450(BasicStructuralSteel):
    name: str = "S450"
    f_y_thin: Pascal = field(default_factory=lambda: 440 * N() / mm2())
    f_u_thin: Pascal = field(default_factory=lambda: 550 * N() / mm2())
    f_y_thick: Pascal = field(default_factory=lambda: 410 * N() / mm2())
    f_u_thick: Pascal = field(default_factory=lambda: 550 * N() / mm2())
    norm: str = "EN 10025-2"


"""
Constants
"""

STEEL_TYPES = {"S235": S235, "S275": S275, "S355": S355, "S450": S450}

"""
Definitions
"""


def get(
    steel_type: str, thickness_less_than_equal_40mm: bool = True
) -> BasicStructuralSteel:
    if steel_type not in STEEL_TYPES.keys():
        raise ValueError(f"Steel material '{steel_type}' not in library")
    material: Type[BasicStructuralSteel] = \
        STEEL_TYPES[steel_type]
    return material(thickness_less_than_equal_40mm)
