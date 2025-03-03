"""
Eurocodedesign constants module

Module for easy wrangling with unit values.

Examples
-------
>>> from eurocodedesign.constants import (kN, m, cm2, N)
>>> 5*kN + 3*N
5003.0
>>> 1*N*m
1.0
>>> 100*cm2
0.01
"""

from __future__ import annotations

from math import pi
from abc import ABC
from enum import Enum, unique, auto
from functools import partial
import sys
from typing import TypeAlias, Type, Optional, overload, Any

from eurocodedesign.core.typing import Kilogram, Newton, Pascal, Newtonmeter, \
    Joule, Meter, Meter_2, Meter_3, Meter_4, Seconds, Kelvin, Ampere, Radian

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def isclose(a: Any,
            b: Any,
            rtol: float = 1e-05,
            atol: float = 1e-08) -> bool:
    return (abs(float(a) - float(b)) <=
            (atol + rtol * abs(float(b))))

# SI Base Units as floats, analogue to scipy.constants (package not required)
rad: Radian = 1.0
s: Seconds = 1.0
kg: Kilogram = 1.0
N: Newton = 1.0
m: Meter = 1.0
m2: Meter_2 = 1.0
m3: Meter_3 = 1.0
m4: Meter_4 = 1.0
Pa: Pascal = 1.0
J: Joule = 1.0
K: Kelvin = 1.0
A: Ampere = 1.0

# mass in kg
t = 1e3*kg  # tonne
g = 1e-3*kg # gram

# angle in rad
deg = pi/180*rad # degree. Attention, not degree celsius
# 1 rad/s is not the same as 1 Hz but have the same float representation

# time in seconds
min = 60*s   # minute
h   = 60*min # hour
d   = 24*h   # day
a   = 365*d  # year
Hz  = 1/s    # hertz

# length in meter
km = 1e3*m  # kilometer
dm = 1e-1*m # decimeter
cm = 1e-2*m # centimeter
mm = 1e-3*m # millimeter

# pressure in pascal
GPa = 1e9*Pa
MPa = 1e6*Pa
N_per_mm2 = 1*MPa
kN_per_m3 = 1e3*N/m3
bar = 0.1*MPa
mbar = 1e-3*bar

# area in meter**2
cm2 = 1*cm**2
mm2 = 1*mm**2
cm3 = 1*cm**3
mm3 = 1*mm**3
cm4 = 1*cm**4
mm4 = 1*mm**4

# volume in meter**3
L = 1e-3*m3 # liter
mL = 1e-3*L # milliliter

# speed in meter per second
kmh = 1*km/h

# energy in joule/torque in newtonmeter
Nm  = 1*N*m
kNm = 1e3*Nm

# power in watt
W = 1*J/s
V = 1*W/A
kV = 1e3*V
mV = 1e-3*V

# force in newton
kN = 1e3*N




