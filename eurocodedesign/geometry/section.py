"""
classes for sections of various materials
"""
from abc import ABC
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BasicSection(ABC):
    name: str = field(compare=False)
