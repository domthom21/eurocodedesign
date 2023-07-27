"""
Thread-safe module for collecting printable information on calculation steps

Examples
    from eurocodedesign import stepper
    >>> with stepper.create() as st1:
    >>>    section = "IPE300"
    >>>    st1.step(f"Steel section {section} has height 3.0 m.")
    >>>    # do stuff
    >>>    st1.step(f"{section} is of cross-section type {QK}.")
    Steel section IPE300 has height 3.0 m. IPE300 is of cross-section type QK3.
    >>> st2 = stepper.create()
    >>> st2.step("Add step")
    >>> del st2
    Add step
"""
from collections import deque
from functools import wraps
from types import TracebackType
import sys
from typing import Callable, TypeVar, ParamSpec
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from eurocodedesign.config import config


class Stepper:
    """
    Thread-safe context manager for collection of calculation steps
    """

    def __init__(self, output: bool) -> None:
        self.output: bool = output
        self._steps: deque[str] = deque()

    def __str__(self) -> str:
        """
        Returns: Added steps concatenated to one string separated by spaces.
        """
        return ' '.join(self._steps)

    def get_steps(self) -> deque[str]:
        """
        Returns: Current steps as deque
        """
        return self._steps

    def step(self, description: str) -> None:
        """ Method for adding a calculation step
        Args:
            description: Description of a step to add

        Returns: None

        """
        self._steps.append(description)

    def __enter__(self) -> Self:
        return self

    def _flush(self) -> None:
        if not self.output:
            return
        string = str(self)
        if string:
            print(self)
        self._steps.clear()

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        self._flush()

    def __del__(self) -> None:
        self._flush()


def create(output: bool | None = None) -> Stepper:
    """
    Factory method to create a new stepper object

    Returns: New Stepper object

    """
    if output is not None:
        return Stepper(output)
    return Stepper(config['stepper']['output'])


_P = ParamSpec('_P')
_T = TypeVar('_T')


def inject_stepper(func: Callable[_P, _T]) -> Callable[_P, _T]:
    """Decorator for automatic injection of a stepper object

    Expects a function parameter "stepper" in func for injection.
    Uses factory method stepper.create() without parameters.
    """
    @wraps(func)
    def _wrapper(*args: _P.args, **kwds: _P.kwargs) -> _T:
        if 'stepper' not in kwds:
            kwds['stepper'] = create()
        return func(*args, **kwds)
    return _wrapper
