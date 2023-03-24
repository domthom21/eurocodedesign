""" Material properties of structural steel 

Classes defining the different types of construction steel that are permitted 
with in the Eurocode framework. The different steel types are defined by the
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
    steel_material = ss.get("S235", True) # S235 steel material with thickness <= 40 mm
    steel_material = ss.get("S355", False) # S355 steel material with thickness >= 40 mm
    
    yield_stress = steel_material.fy
    ultimate_stress = steel_material.fu
    
    elastic_modulus = steel_material.E 
    shear_modulus = steel_material.G
    thermal_coefficient = steel_material.alpha  
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BasicStructuralSteel:
    _thickness_less_than_equal_40mm: bool = True
    _elastic_modulus: float = field(default=210_000, kw_only=True)
    _shear_modulus: float = field(default=81_000, kw_only=True)
    _thermal_coefficient: float = field(default=1.2e-7, kw_only=True)  # 1/K
    poissons_ratio: float = field(default=0.3, kw_only=True)

    @property
    def fy(self):
        if self._thickness_less_than_equal_40mm:
            return self._fy_thin
        else:
            return self._fy_thick

    @property
    def fu(self):
        if not self._thickness_less_than_equal_40mm:
            return self._fu_thin
        else:
            return self._fu_thick

    @property
    def E(self):
        return self._elastic_modulus

    @property
    def G(self):
        return self._shear_modulus

    @property
    def alpha(self):
        return self._thermal_coefficient


@dataclass(frozen=True)
class S235(BasicStructuralSteel):
    name: float = field(default="S235", kw_only=True)
    _fy_thin: float = field(default=235, kw_only=True)
    _fu_thin: float = field(default=360, kw_only=True)
    _fy_thick: float = field(default=215, kw_only=True)
    _fu_thick: float = field(default=360, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S275(BasicStructuralSteel):
    name: float = field(default="S275", kw_only=True)
    _fy_thin: float = field(default=275, kw_only=True)
    _fu_thin: float = field(default=430, kw_only=True)
    _fy_thick: float = field(default=255, kw_only=True)
    _fu_thick: float = field(default=410, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S355(BasicStructuralSteel):
    name: float = field(default="S355", kw_only=True)
    _fy_thin: float = field(default=355, kw_only=True)
    _fu_thin: float = field(default=490, kw_only=True)
    _fy_thick: float = field(default=335, kw_only=True)
    _fu_thick: float = field(default=470, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S450(BasicStructuralSteel):
    name: float = field(default="S450", kw_only=True)
    _fy_thin: float = field(default=440, kw_only=True)
    _fu_thin: float = field(default=550, kw_only=True)
    _fy_thick: float = field(default=410, kw_only=True)
    _fu_thick: float = field(default=550, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


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
    return STEEL_TYPES[steel_type](thickness_less_than_equal_40mm)


if __name__ == "__main__":
    steel = get("s121")
