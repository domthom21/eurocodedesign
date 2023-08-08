"""
Package for type declarations
"""
from typing import TypeAlias, Sequence, Tuple

from eurocodedesign.units import Pascal

FloatSequence: TypeAlias = Sequence[float]
FloatTriple: TypeAlias = Tuple[float, float, float]
PascalSequence: TypeAlias = Sequence[Pascal]

"""TypeAlias for the load factor ```\\eta`` """
Eta: TypeAlias = float
