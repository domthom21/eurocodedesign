"""
Package for type declarations
"""
from typing import TypeAlias, Sequence, Tuple

# SI Base Units, analogue to scipy.constants (package not required)
Radian: TypeAlias = float
Seconds: TypeAlias = float
Hertz: TypeAlias = float
Meter: TypeAlias = float
Meter_2: TypeAlias = float
Meter_3: TypeAlias = float
Meter_4: TypeAlias = float
Kilogram: TypeAlias = float
Newton: TypeAlias = float
Pascal: TypeAlias = float
Joule: TypeAlias = float
Newtonmeter = Joule
Kelvin: TypeAlias = float
Ampere: TypeAlias = float

Meter_per_Second: TypeAlias = float
Meter_per_Second_2: TypeAlias = float
Newton_per_Meter: TypeAlias = float


FloatSequence: TypeAlias = Sequence[float]
FloatTriple: TypeAlias = Tuple[float, float, float]
MeterTriple: TypeAlias = Tuple[Meter, Meter, Meter]
PascalSequence: TypeAlias = Sequence[Pascal]

r"""TypeAlias for the load factor :math:`\eta` """
Eta: TypeAlias = float
