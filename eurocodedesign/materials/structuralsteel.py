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

# todo: add example of how to get properties for different thickness 
# todo: materials
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BasicStructuralSteel:
    thickness_less_than_40mm: bool = True
    elastic_modulus: float = field(default=210_000, kw_only=True)
    shear_modulus: float = field(default=81_000, kw_only=True)
    poissons_ratio: float = field(default=0.3, kw_only=True)
    thermal_coefficient: float = field(default=1.2e-7, kw_only=True)  # 1/K

    @property
    def fy(self):
        if self.thickness_less_than_40mm:
            return self.fy_thin
        else:
            return self.fy_thick

    @property
    def fu(self):
        if not self.thickness_less_than_40mm:
            return self.fu_thin
        else:
            return self.fu_thick


@dataclass(frozen=True)
class S235(BasicStructuralSteel):
    name: float = field(default="S235", kw_only=True)
    fy_thin: float = field(default=235, kw_only=True)
    fu_thin: float = field(default=360, kw_only=True)
    fy_thick: float = field(default=215, kw_only=True)
    fu_thick: float = field(default=360, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S275(BasicStructuralSteel):
    name: float = field(default="S275", kw_only=True)
    fy_thin: float = field(default=275, kw_only=True)
    fu_thin: float = field(default=430, kw_only=True)
    fy_thick: float = field(default=255, kw_only=True)
    fu_thick: float = field(default=410, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S355(BasicStructuralSteel):
    name: float = field(default="S355", kw_only=True)
    fy_thin: float = field(default=355, kw_only=True)
    fu_thin: float = field(default=490, kw_only=True)
    fy_thick: float = field(default=335, kw_only=True)
    fu_thick: float = field(default=470, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


@dataclass(frozen=True)
class S450(BasicStructuralSteel):
    name: float = field(default="S450", kw_only=True)
    fy_thin: float = field(default=440, kw_only=True)
    fu_thin: float = field(default=550, kw_only=True)
    fy_thick: float = field(default=410, kw_only=True)
    fu_thick: float = field(default=550, kw_only=True)
    norm: str = field(default="EN 10025-2", kw_only=True)


""" 
constants
"""

STEEL_TYPES = {"S235": S235, "S275": S275, "S355": S355, "S450": S450}


""" 
definitions
"""

def get(steel_type: str) -> BasicStructuralSteel:
    pass


if __name__ == "__main__":
    steel = S235(24)
    print(steel.thickness)
