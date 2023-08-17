from eurocodedesign.standard import ec3


def test_gamma_M0():
    assert ec3.gamma_M0() == 1.00


def test_gamma_M1():
    assert ec3.gamma_M1() == 1.00


def test_gamma_M2():
    assert ec3.gamma_M2() == 1.25
