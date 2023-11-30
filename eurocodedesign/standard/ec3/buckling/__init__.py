from enum import Enum, auto
from typing import Dict

import numpy as np


class BucklingLine(Enum):
    a_0 = auto()
    a = auto()
    b = auto()
    c = auto()
    d = auto()


def get_alpha(buckling_line: BucklingLine) -> float:
    _imperfection_value: Dict[BucklingLine, float] = {
        BucklingLine.a_0: 0.13,
        BucklingLine.a: 0.21,
        BucklingLine.b: 0.34,
        BucklingLine.c: 0.49,
        BucklingLine.d: 0.76,
    }
    return _imperfection_value[buckling_line]


def _calc_Phi(bar_lambda: float, buckling_line: BucklingLine) -> float:
    # according to EC3-1-1 6.3.1.2
    alpha: float = get_alpha(buckling_line)
    Phi: float = 0.5 * (1 + alpha * (bar_lambda - 0.2) + bar_lambda ** 2)
    return Phi


def calc_chi(bar_lambda: float, buckling_line: BucklingLine) -> float:
    # according to EC3-1-1 6.3.1.2 bar lambda relative slenderness
    chi: float
    if bar_lambda <= 0.2:
        chi = 1.0
    else:  # bar_lambda > 0.2
        Phi: float = _calc_Phi(bar_lambda, buckling_line)
        chi = 1 / (Phi + np.sqrt(Phi ** 2 - bar_lambda ** 2))
        chi = min(chi, 1.0)
    return chi
