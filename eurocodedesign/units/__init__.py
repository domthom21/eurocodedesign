"""
Eurocodedesign unit module

Module for easy wrangling with unit values.

Examples
-------
>>> from eurocodedesign.units import (kN, m, cm2, N)
>>> 5*kN() + 3*N()
5003.0 N
>>> N() + m()
TypeError: Addition not allowed for type <class 'eurocodedesign.units.Newton'>
 and <class 'eurocodedesign.units.Meter'>
>>> N()*m()
1.0 J
>>> 100*cm2()
100.0 cm²
"""

from __future__ import annotations
from abc import ABC
from enum import Enum, unique, auto
from functools import partial
import sys
from typing import TypeAlias, Type, Optional, overload, Any


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@unique
class PhysicalType(Enum):
    ANGLE = auto()
    TIME = auto()
    LENGTH = auto()
    AREA = auto()
    VOLUME = auto()
    SECOND_MOMENT_OF_AREA = auto()
    SPEED = auto()
    ACCELERATION = auto()
    MASS = auto()
    FORCE = auto()
    STIFFNESS = auto()
    PRESSURE = auto()
    ENERGY = auto()
    TEMPERATURE = auto()


class Prefix(float, Enum):
    "Metric prefixes from nano (1e-9) to giga (1e9)"
    G = giga = 1e9
    M = mega = 1e6
    k = kilo = 1e3
    h = hecto = 1e2
    da = deca = 1e1
    none = one = 1e0
    d = deci = 1e-1
    c = centi = 1e-2
    m = milli = 1e-3
    µ = micro = 1e-6
    n = nano = 1e-9


def isclose(a: Any,
            b: Any,
            rtol: float = 1e-05,
            atol: float = 1e-08) -> bool:
    if type(a) is not type(b):
        raise TypeError
    return (abs(a.to_numeric() - b.to_numeric()) <=
            (atol + rtol * abs(b.to_numeric())))


Seconds: TypeAlias = float
Meter: TypeAlias = float
Meter_2: TypeAlias = float
Meter_3: TypeAlias = float
Meter_4: TypeAlias = float
Kilogram: TypeAlias = float
Newton: TypeAlias = float
Pascal: TypeAlias = float
Joule: TypeAlias = float
Kelvin: TypeAlias = float

Meter_per_Second: TypeAlias = float
Meter_per_Second_2: TypeAlias = float
Newton_per_Meter: TypeAlias = float

N: TypeAlias = Newton
m: TypeAlias = Meter
m2: TypeAlias = Meter_2
m3: TypeAlias = Meter_3
m4: TypeAlias = Meter_4
Pa: TypeAlias = Pascal
Newtonmeter: TypeAlias = Joule
Nm: TypeAlias = Joule
J: TypeAlias = Joule


centimeter = Prefix.centi*m(1)
cm = centimeter
millimeter = Prefix.milli*m(1)
mm = millimeter

square_centimeter = centimeter**2
cm2 = square_centimeter
square_millimeter = millimeter**2
mm2 = square_millimeter
cubic_centimeter = centimeter**3
cm3 = cubic_centimeter
cubic_millimeter = millimeter**3
mm3 = cubic_millimeter
quartic_centimeter = centimeter**4
cm4 = quartic_centimeter
quartic_millimeter = millimeter**4
mm4 = quartic_millimeter


kiloNewton = Prefix.kilo*N(1)
kN = kiloNewton

GigaPascal = Prefix.giga*N(1)
MegaPascal = Prefix.mega*N(1)
MPa = MegaPascal
N_per_mm2 = MegaPascal
GPa = GigaPascal
