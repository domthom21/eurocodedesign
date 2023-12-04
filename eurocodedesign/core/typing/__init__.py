"""
Package for type declarations
"""
from typing import TypeAlias, Sequence, Tuple

from eurocodedesign.units import Pascal, Meter

FloatSequence: TypeAlias = Sequence[float]
FloatTriple: TypeAlias = Tuple[float, float, float]
MeterTriple: TypeAlias = Tuple[Meter, Meter, Meter]
PascalSequence: TypeAlias = Sequence[Pascal]
NACountry: TypeAlias = str | None

"""TypeAlias for the load factor ```\\eta`` """
Eta: TypeAlias = float
