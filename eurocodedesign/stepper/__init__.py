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
import sys
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class Stepper:
    """
    Thread-safe context manager for collection of calculation steps
    """

    def __init__(self) -> None:
        self._steps: deque = deque()

    def __str__(self) -> str:
        """
        Returns: Added steps concatenated to one string separated by spaces.
        """
        return ' '.join(self._steps)

    def get_steps(self) -> deque:
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
        string = str(self)
        if string:
            print(self)
        self._steps.clear()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._flush()

    def __del__(self) -> None:
        self._flush()


def create() -> Stepper:
    """
    Factory method to create a new stepper object

    Returns: New Stepper object

    """
    return Stepper()
