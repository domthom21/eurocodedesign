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
    return _imperfection_value.get(buckling_line)

# according to EC3-1-1 6.3.1.2
def _calc_Phi(bar_lambda, buckling_line: BucklingLine) -> float:
    alpha: float = get_alpha(buckling_line)
    Phi: float = 0.5 * (1 + alpha * (bar_lambda - 0.2) + bar_lambda ** 2)
    return Phi


# according to EC3-1-1 6.3.1.2 bar lamdda relative slenderness
def calc_chi(bar_lambda: float, buckling_line: BucklingLine) -> float:
    chi: float
    if bar_lambda <= 0.2:
        chi = 1.0
    else: # bar_lambda > 0.2
        Phi = _calc_Phi(bar_lambda, buckling_line)
        chi = 1 / (Phi + np.sqrt(Phi ** 2 - bar_lambda ** 2))
        chi = min(chi, 1.0)
    return chi

