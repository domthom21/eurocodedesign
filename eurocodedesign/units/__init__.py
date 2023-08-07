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
from typing import TypeAlias, Type, Optional, overload

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
    PRESSURE = auto()
    ENERGY = auto()
    TEMPERATURE = auto()


class Prefix(Enum):
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


class AbstractUnit(ABC):
    _unit_str: str
    _power = 1
    _physical_type: PhysicalType

    def _is_prefix_allowed(self, type: PhysicalType) -> bool:
        return type not in (PhysicalType.TIME,
                            PhysicalType.ANGLE,
                            PhysicalType.MASS,
                            PhysicalType.TEMPERATURE)

    def __init__(self, value: float = 1.0, prefix: Prefix = Prefix.none):
        if (prefix != Prefix.none and
                not self._is_prefix_allowed(self._physical_type)):
            raise ValueError(f'Metric prefix {prefix} not supported'
                             f' for type {type(self)}')
        self._unit: Type[AbstractUnit] = self.__class__
        self._prefix: Prefix = prefix
        self._value: float = value * float(prefix.value ** self._power)

    def __str__(self) -> str:
        value = self._value / (self._prefix.value ** self._power)
        prefix = self._prefix.name if self._prefix != Prefix.none else ''
        return f"{value} {prefix}{self._unit_str}"

    def __repr__(self) -> str:
        """Notebook and console-friendly output of the unit value

        Returns: Unit as string

        """
        return str(self)

    def __repr_latex_(self) -> None:
        raise NotImplementedError

    def __add__(self, other: Self) -> Self:
        if (not isinstance(other, self) or
                self._physical_type != other._physical_type):
            raise TypeError(f'Addition not allowed for'
                            f' type {type(self)} and {type(other)}')
        return type(self)(self._value + other._value)

    def __sub__(self, other: Self) -> Self:
        if (not isinstance(other, self) or
                self._physical_type != other._physical_type):
            raise TypeError(f'Subtraction not allowed for '
                            f'type {type(self)} and {type(other)}')
        return type(self)(self._value - other._value)

    def __mul__(self, other: object) -> AbstractUnit:
        """
        Multiplication of a unit type with another unit

        Only valid if multiplication with other unit is supported or
        other value is of type float or int
        Args:
            other:

        Returns:

        """
        if isinstance(other, (int, float)):
            return type(self)(self._value * other /
                              (self._prefix.value
                               ** self._power), self._prefix)
        if not isinstance(other, AbstractUnit):
            raise TypeError(f"Multiplication not allowed for"
                            f" type {type(self)} and {type(other)}.")
        self_type = type(self)
        other_type = type(other)
        new_type: Optional[Type[AbstractUnit]] = \
            _allowed_multiplications.get((self_type, other_type))
        # check other order because tuple dict keys are ordered
        if not new_type:
            new_type = _allowed_multiplications.get(
                (other_type, self_type))
        if not new_type:
            raise TypeError(f"Multiplication not allowed for"
                            f" type {self_type} and {other_type}.")
        return new_type(self._value * other._value)

    def __rmul__(self, other: object) -> AbstractUnit:
        return self * other

    # todo extend overloads
    @overload
    def __truediv__(self, other: Meter) -> float: ...
    @overload
    def __truediv__(self, other: Meter_2) -> Pascal: ...
    @overload
    def __truediv__(self, other: Pascal) -> float: ...
    @overload
    def __truediv__(self, other: Meter_3) -> Pascal: ...
    @overload
    def __truediv__(self, other: object) -> AbstractUnit | float: ...

    def __truediv__(self, other: object) -> AbstractUnit | float:
        if isinstance(other, (int, float)):
            return type(self)(self._value
                              / other
                              / (self._prefix.value
                                 ** self._power), self._prefix)
        if not isinstance(other, AbstractUnit):
            raise TypeError('No divisions by another unit allowed'
                            f' for f{type(self)}')
        self_type = type(self)
        other_type = type(other)

        if self_type == other_type:
            return float(self._value/other._value)

        if self_type not in _allowed_multiplications.values():
            raise TypeError('No divisions by another unit allowed'
                            f' for f{self_type}')
        keys = [k for k, v in _allowed_multiplications.items()
                if v == self_type]
        for type_pair in keys:
            if other_type in type_pair:
                l_ = list(type_pair)
                l_.remove(other_type)
                new_type = l_[0]
                return new_type(self._value / other._value)
        raise TypeError(f'Division of {self_type} by '
                        f'{other_type} not allowed.')

    def __lt__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError
        return self._value < other._value

    def __le__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError
        return self._value <= other._value

    def __eq__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError('Self type: ', type(self), 'Other type: ',
                            type(other))
        return self._value == other._value

    def __ne__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError
        return not (self == other)

    def __ge__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError
        return self._value >= other._value

    def __gt__(self, other: object) -> bool:
        if (not isinstance(other, AbstractUnit) or
                self._physical_type != other._physical_type):
            raise TypeError
        return self._value > other._value

    def to(self, prefix: Prefix) -> None:
        """Convert unit prefix to given prefix

        Args:
            prefix:

        Returns: None

        """
        if not self._is_prefix_allowed(self._physical_type):
            raise TypeError(f"Prefix {prefix} not allowed for {type(self)}")
        self._prefix = prefix
        return

    def to_numeric(self) -> float:
        """
        Return the unit value as float of base unit
        Returns: Current unit value as float

        Examples
        >>> (3*kN()).to_numeric()
        3000.0

        """
        return float(self._value)


class Seconds(AbstractUnit):
    _physical_type = PhysicalType.TIME
    _unit_str = "s"


class Meter(AbstractUnit):
    _physical_type = PhysicalType.LENGTH
    _unit_str = "m"


class Meter_2(AbstractUnit):
    _power = 2
    _physical_type = PhysicalType.AREA
    _unit_str = "m²"


class Meter_3(AbstractUnit):
    _power = 3
    _physical_type = PhysicalType.VOLUME
    _unit_str = "m³"


class Meter_4(AbstractUnit):
    _power = 4
    _physical_type = PhysicalType.SECOND_MOMENT_OF_AREA
    _unit_str = "m⁴"


class Meter_per_Second(AbstractUnit):
    _physical_type = PhysicalType.SPEED
    _unit_str = "m/s"


class Meter_per_Second_2(AbstractUnit):
    _physical_type = PhysicalType.ACCELERATION
    _unit_str = "m/s²"


class Kilogram(AbstractUnit):
    _physical_type = PhysicalType.MASS
    _unit_str = "kg"


class Newton(AbstractUnit):
    _physical_type = PhysicalType.FORCE
    _unit_str = "N"


class Pascal(AbstractUnit):
    _physical_type = PhysicalType.PRESSURE
    _unit_str = "Pa"


class Joule(AbstractUnit):
    _physical_type = PhysicalType.ENERGY
    _unit_str = "J"


class Kelvin(AbstractUnit):
    _physical_type = PhysicalType.TEMPERATURE
    _unit_str = "K"


_allowed_multiplications = {
    (Meter, Meter): Meter_2,
    (Meter_2, Meter): Meter_3,
    (Meter_2, Meter_2): Meter_4,
    (Meter_3, Meter): Meter_4,
    (Meter_per_Second, Seconds): Meter,
    (Meter_per_Second_2, Seconds): Meter_per_Second,
    (Kilogram, Meter_per_Second_2): Newton,
    (Pascal, Meter_2): Newton,
    (Newton, Meter): Joule,
}

N: TypeAlias = Newton
m: TypeAlias = Meter
m2: TypeAlias = Meter_2
m3: TypeAlias = Meter_3
m4: TypeAlias = Meter_4
Pa: TypeAlias = Pascal
Newtonmeter: TypeAlias = Joule
Nm: TypeAlias = Joule
J: TypeAlias = Joule


centimeter = partial(Meter, prefix=Prefix.centi)
cm = centimeter
millimeter = partial(Meter, prefix=Prefix.milli)
mm = millimeter

square_centimeter = partial(Meter_2, prefix=Prefix.centi)
cm2 = square_centimeter
square_millimeter = partial(Meter_2, prefix=Prefix.milli)
mm2 = square_millimeter
cubic_centimeter = partial(Meter_3, prefix=Prefix.centi)
cm3 = cubic_centimeter
cubic_millimeter = partial(Meter_3, prefix=Prefix.milli)
mm3 = cubic_millimeter
quartic_centimeter = partial(Meter_4, prefix=Prefix.centi)
cm4 = quartic_centimeter
quartic_millimeter = partial(Meter_4, prefix=Prefix.milli)
mm4 = quartic_millimeter


kiloNewton = partial(Newton, prefix=Prefix.kilo)
kN = kiloNewton

GigaPascal = partial(Pascal, prefix=Prefix.giga)
MegaPascal = partial(Pascal, prefix=Prefix.mega)
MPa = MegaPascal
N_per_mm2 = MegaPascal
GPa = GigaPascal
