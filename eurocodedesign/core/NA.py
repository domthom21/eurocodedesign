"""
National annex module

This module enables the use of setting the country code from which national
defined parameters should be used. NDP-supporting functions are annotated with
the @NDP decorator.

Example:
    ::

        >>> from eurocodedesign.core.NA import set_country
        >>> import eurocodedesign.standard.ec3 as ec3
        >>> ec3.gamma_M1()
        ... 1.00
        >>> set_country('de')
        >>> ec3.gamma_M1()
        ... 1.10
        >>> ec3.gamma_M1(country=None)
        ... 1.00
        >>> set_country('')
        >>> with ed.core.NA.CountryContext(country='de'):
        >>>     ec3.gamma_M1()
        ... 1.10
        >>> ec3.gamma_M1()
        ... 1.00

"""
from enum import Enum, unique
from functools import wraps
from types import TracebackType
from typing import ParamSpec, TypeVar, Callable
import pandas as pd
from pathlib import Path

import eurocodedesign.config as cf

_P = ParamSpec('_P')
_T = TypeVar('_T')


@unique
class NACountry(Enum):
    """Enum for representing the supported national annexes

    Country code according to ISO-3166-1 ALPHA-2 or empty string
    """
    NONE = ''
    DE = 'DE'


def NDP(func: Callable[_P, _T]) -> Callable[_P, _T]:
    """Decorator for functions supporting NDPs

    This decorator indicates if the following function supports national
    defined parameters (NDPs). The function must support a `country` argument
    for setting the national annex manually and must contain code which
    respects the national annex.

    Args:
        func: the function to wrap

    Returns: the wrapped function
    """
    @wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        return func(*args, **kwargs)
    return wrapper


def set_country(country: NACountry = NACountry.NONE) -> None:
    """Set the national annex country code

    If no country code is given, the national annex is neglected and given
    values from the main standard are taken.

    If no national defined parameters exists, each called function looking
     for a NDP raises a ValueError.

    Args:
        country: country code according to ISO-3166-1 ALPHA-2 or empty string

    Returns: None
    """

    cf.config['standard']['_NA']['country'] = country.value


def get_country() -> NACountry:
    return NACountry(cf.config['standard']['_NA']['country'])


class CountryContext:
    """Simple context manager for setting the country locally"""
    def __init__(self, country: NACountry = NACountry.NONE) -> None:
        self.country: NACountry = country

    def __enter__(self) -> None:
        self.old_country: NACountry = get_country()
        set_country(self.country)

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        set_country(self.old_country)


def load_NDP(key: str,
             default: str = '',
             country: NACountry = NACountry.NONE) -> str:
    """Load a specific NDP by key from country

    Conversion to float or int must be done by user

    If country is an empty string, country from global config is taken.
    If this is also empty, the default value is returned

    Args:
        key: key of NDP to load
        default: default value to use
        country: country code according to ISO-3166-1 ALPHA-2

    Returns: NDP or default value as string

    Raises:
        NotImplementedError if no national annex data for given country exist
         or if no NDP with given key exist

    """
    if country is NACountry.NONE:
        country = get_country()
    # if still no country set, return default value
    if country is NACountry.NONE:
        return default
    file = str(country.value) + '.csv'
    path = Path(__file__).parent.parent / 'standard' / '_NA' / file
    try:
        df = pd.read_csv(path, index_col="NDP_key")
        value = df.at[key, 'value']
    except KeyError:
        raise NotImplementedError(f"NDP not implemented for country {country}"
                                  f" and NDP key {key}.")
    return str(value)
