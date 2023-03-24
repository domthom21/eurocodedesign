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
class BasicSteel:
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
class S235(BasicSteel):
    name: float = field(default="S235", kw_only=True)
    fy_thin: float = field(default=235, kw_only=True)
    fu_thin: float = field(default=360, kw_only=True)
    fy_thick: float = field(default=215, kw_only=True)
    fu_thick: float = field(default=360, kw_only=True)


if __name__ == "__main__":
    steel = S235(24)
    print(steel.thickness)
