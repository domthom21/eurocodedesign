from enum import Enum, auto

from eurocodedesign.materials.structuralsteel import BasicStructuralSteel


class PlateSupport(Enum):
    """ Class for differentiation between one-side and two-side supported
    buckling fields according to EN 1993-1-5 §4.4
    """
    ONE_SIDE = auto()
    TWO_SIDE = auto()


class PlateStiffeners(Enum):
    """ Class for differentiation of different stiffener types"""
    NONE = auto()
    RIGID = auto()
    NON_RIGID = auto()


def get_eta(steel_grade: BasicStructuralSteel) -> float:
    """Get eta according to EC3-1-5

    Args:
        steel_grade: Steel grade

    Returns: Eta

    """
    eta: float = 1.2 if steel_grade.name <= "S460" else 1.0
    return eta
