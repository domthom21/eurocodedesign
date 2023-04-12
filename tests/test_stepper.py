import pytest

from eurocodedesign import stepper


def test_stepper(capsys):
    section = "IPE300"
    height = "3.0 m"
    width = "2.5 m"
    x = 42
    QK = "QK3"
    with stepper.create() as st:
        st.step(f"Steel section {section} has height {height} and width {width}.")
        # do stuff
        st.step(f"Because of {x}, {section} is of cross-section type {QK}.")
    captured = capsys.readouterr()
    result = r"Steel section IPE300 has height 3.0 m and width 2.5 m. " \
             "Because of 42, IPE300 is of cross-section type QK3.\n"
    assert captured.out == result


