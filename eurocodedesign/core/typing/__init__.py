"""
Package for type declarations
"""
from typing import TypeAlias, Sequence, Tuple

from eurocodedesign.units import Pascal, Meter

FloatSequence: TypeAlias = Sequence[float]
FloatTriple: TypeAlias = Tuple[float, float, float]
MeterTriple: TypeAlias = Tuple[Meter, Meter, Meter]
PascalSequence: TypeAlias = Sequence[Pascal]

r"""TypeAlias for the load factor :math:`\eta` """
Eta: TypeAlias = float
