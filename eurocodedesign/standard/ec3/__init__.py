


def gamma_M0() -> float:
    """
    Partial factor ``\\gamma_{M0}`` for buildings

    Partial factor for resistance of cross-sections (whatever the class is).
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: ``\\gamma_{M0}``

    """
    gamma_M0 = 1.00
    return gamma_M0


def gamma_M1() -> float:
    """
    Partial factor ``\\gamma_{M1}`` for buildings

    Partial factor for resistance of members to instability assessed by
    member checks.
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: ``\\gamma_{M1}``

    """
    gamma_M1 = 1.00
    return gamma_M1


def gamma_M2() -> float:
    """
    Partial factor ``\\gamma_{M2}`` for buildings

    Partial factor for resistance of cross-sections in tension to fracture.
    Value according to EN 1993-1-1:2010-12 §6.1 (1)

    Returns: ``\\gamma_{M2}``

    """
    gamma_M2 = 1.25
    return gamma_M2
