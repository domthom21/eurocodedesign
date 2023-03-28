from abc import ABC
from enum import Enum, unique, auto
from functools import partial
from typing import Self, TypeAlias


@unique
class PhysicalType(Enum):
    DIMENSIONLESS = auto()
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
    giga = G = 1e9
    mega = M = 1e6
    kilo = k = 1e3
    hecto = h = 1e2
    deca = da = 1e1
    none = one = 1e0
    deci = d = 1e-1
    centi = c = 1e-2
    milli = m = 1e-3
    micro = µ = 1e-6
    nano = n = 1e-9


_allowed_multiplications = {}


class AbstractUnit(ABC):
    _value: float = 1.0
    _prefix: Prefix = Prefix.none
    _unit: Self
    _power = 1
    _physical_type: PhysicalType

    def _is_prefix_allowed(type: PhysicalType):
        return type not in (PhysicalType.TIME,
                            PhysicalType.ANGLE,
                            PhysicalType.MASS,
                            PhysicalType.TEMPERATURE)

    def __init__(self, value: float = 1.0, prefix: Prefix = Prefix.none):
        if (prefix != Prefix.none and
            not self._is_prefix_allowed(self._physical_type)):
            raise ValueError(f'Metric prefix {prefix} not supported'
                             f' for type {type(self)}')
        self._unit = self.__class__
        self._prefix = prefix
        self._value = value * float(prefix.value ** self._power)

    def __str__(self):
        value = self._value / (self._prefix.value ** self._power)
        prefix = self._prefix.name if self._prefix != Prefix.none else ''
        return f"{value} {prefix}{self._unit.__name__}"

    def __repr__(self):
        raise NotImplementedError

    def __repr_latex_(self):
        raise NotImplementedError

    def __add__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError(f'Addition not allowed for'
                            f' type {type(self)} and {type(other)}')
        return type(self)(self._value + other._value, self._prefix)

    def __sub__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError(f'Subtraction not allowed for '
                            f'type {type(self)} and {type(other)}')
        return type(self)(self._value - other._value, self._prefix)

    def __mul__(self, other: Self | float | int):
        if isinstance(other, (int, float)):
            return type(self)(self._value * other /
                              (self._prefix.value
                               ** self._power), self._prefix)
        self_type = type(self)
        other_type = type(other)
        new_type = _allowed_multiplications.get((self_type, other_type), False)
        # check other order because tuple dict keys are ordered
        if not new_type:
            new_type = _allowed_multiplications.get(
                (other_type, self_type), False)
        if not new_type:
            raise TypeError(f"Multiplication not allowed for"
                            f" type {self_type} and {other_type}.")
        return new_type(self._value * other._value)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other: Self | float | int):
        if isinstance(other, (int, float)):
            return type(self)(self._value
                              / other
                              / (self._prefix.value
                                 ** self._power), self._prefix)
        self_type = type(self)
        other_type = type(other)

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

    def __lt__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return self._value < other._value

    def __le__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return self._value <= other._value

    def __eq__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return self._value == other._value

    def __ne__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return not (self == other)

    def __ge__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return self._value >= other._value

    def __gt__(self, other: Self):
        if self._physical_type != other._physical_type:
            raise TypeError
        return self._value > other._value

    def to(self, prefix: Prefix):
        """
        Convert unit prefix to given prefix
        @param prefix: Prefix,
        @return: None
        """
        if not self._is_prefix_allowed(prefix):
            raise TypeError(f"Prefix {prefix} not allowed for {type(self)}")
        self._prefix = prefix
        return


class Seconds(AbstractUnit):
    _physical_type = PhysicalType.TIME


class Meter(AbstractUnit):
    _physical_type = PhysicalType.LENGTH


class Meter_2(AbstractUnit):
    _power = 2
    _physical_type = PhysicalType.AREA


class Meter_3(AbstractUnit):
    _power = 3
    _physical_type = PhysicalType.VOLUME


class Meter_4(AbstractUnit):
    _power = 4
    _physical_type = PhysicalType.SECOND_MOMENT_OF_AREA


class Meter_per_Second(AbstractUnit):
    _physical_type = PhysicalType.SPEED


class Meter_per_Second_2(AbstractUnit):
    _physical_type = PhysicalType.ACCELERATION


class Kilogram(AbstractUnit):
    _physical_type = PhysicalType.MASS


class Newton(AbstractUnit):
    _physical_type = PhysicalType.FORCE


class Pascal(AbstractUnit):
    _physical_type = PhysicalType.PRESSURE


class Joule(AbstractUnit):
    _physical_type = PhysicalType.ENERGY


class Kelvin(AbstractUnit):
    _physical_type = PhysicalType.TEMPERATURE


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

kiloNewton = partial(Newton, prefix=Prefix.kilo)
kN: TypeAlias = kiloNewton

MegaPascal = partial(Pascal, prefix=Prefix.mega)
MPa: TypeAlias = MegaPascal

J: TypeAlias = Joule
