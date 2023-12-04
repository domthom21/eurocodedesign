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

"""
from functools import wraps
from typing import ParamSpec, TypeVar, Callable

from eurocodedesign.core.typing import NACountry

_NA_country: NACountry = None

_P = ParamSpec('_P')
_T = TypeVar('_T')


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


def set_country(country: NACountry) -> None:
    """Set the national annex country code

    If no country code is given, the national annex is neglected and given
    values from the main standard are taken.

    If no national defined parameters exists, each called function looking
     for a NDP raises a ValueError

    Args:
        country: country code according to ISO-3166-1 ALPHA-2 or None

    Returns: None
    """
    global _NA_country
    _NA_country = country


def load_NDP(key: str,
             default: str = '',
             country: NACountry = None) -> str:
    """Load a specific NDP by key from country

    Conversion to float or int must be done by user

    Args:
        key: key of NDP to load
        default: default value to use
        country: country code according to ISO-3166-1 ALPHA-2 or None

    Returns: value as string

    """
    import pandas as pd
    from pathlib import Path

    country = _NA_country if country is None else country
    # No NA in general set, return default value
    if country is None:
        return default
    file = country + '.csv'
    path = Path(__file__).parent.parent / 'standard' / '_NA' / file
    df = pd.read_csv(path, index_col="NDP_key")
    return str(df['value'].get(key, default=default))
