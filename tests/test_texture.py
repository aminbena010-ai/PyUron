import numpy as np
import pytest

from pyuron.graphics.procedural import make_checker


def test_checker_returns_rgba_uint8():
    img = make_checker(width=32, height=32, cell=8)
    assert img.dtype == np.uint8
    assert img.shape == (32, 32, 4)


def test_checker_is_periodic():
    img = make_checker(width=32, height=32, cell=8)
    # Celdas del mismo color (distancia 2*cell = 16)
    assert (img[0, 0] == img[16, 16]).all()
    # Celdas contiguas (distancia cell = 8) tienen color opuesto
    assert (img[0, 0] != img[8, 0]).all()


def test_checker_rejects_invalid_size():
    with pytest.raises(ValueError):
        make_checker(width=0)
    with pytest.raises(ValueError):
        make_checker(cell=0)
