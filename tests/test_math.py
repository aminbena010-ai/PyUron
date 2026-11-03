import numpy as np
import pytest

from pyuron.math import matrix
from pyuron.math.vector import Vector2, Vector3


def test_vector2_arithmetic():
    a = Vector2(1, 2)
    b = Vector2(3, 4)
    assert (a + b).x == pytest.approx(4)
    assert (a + b).y == pytest.approx(6)
    assert (b - a).x == pytest.approx(2)
    assert (a * 3).y == pytest.approx(6)


def test_vector3_length_and_normalize():
    v = Vector3(3, 4, 0)
    assert v.length() == pytest.approx(5.0)
    n = v.normalized()
    assert n.length() == pytest.approx(1.0)


def test_matrix_identity_is_identity():
    m = matrix.identity()
    assert np.allclose(m, np.eye(4))


def test_rotate_z_90_degrees():
    m = matrix.rotate_z(90.0)
    v = np.array([1.0, 0.0, 0.0, 1.0], dtype=np.float32)
    r = m @ v
    assert r[0] == pytest.approx(0.0, abs=1e-6)
    assert r[1] == pytest.approx(1.0, abs=1e-6)


def test_perspective_shape():
    p = matrix.perspective(60.0, 16 / 9, 0.1, 100.0)
    assert p.shape == (4, 4)
    assert p[3, 2] == pytest.approx(-1.0)


def test_ortho_unit_bounds_flips_z_only():
    """ortho(-1,1,-1,1,-1,1) = identidad con Z invertida (convención OpenGL).

    OpenGL niega Z siempre: la cámara mira hacia -Z en vista, pero NDC
    tiene +Z hacia dentro. Es el comportamiento de glOrtho desde 1992.
    """
    o = matrix.ortho(-1, 1, -1, 1, -1, 1)
    expected = np.eye(4, dtype=np.float32)
    expected[2, 2] = -1.0
    assert np.allclose(o, expected)


def test_ortho_maps_corners_to_ndc():
    """Un ortho bien construido lleva las esquinas del frustum a ±1 en NDC."""
    o = matrix.ortho(0, 800, 0, 600, -1, 1)
    # Esquina inferior-izquierda del viewport (0, 0) -> NDC (-1, -1)
    bl = o @ np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
    assert bl[0] == pytest.approx(-1.0)
    assert bl[1] == pytest.approx(-1.0)
    # Esquina superior-derecha (800, 600) -> NDC (1, 1)
    tr = o @ np.array([800.0, 600.0, 0.0, 1.0], dtype=np.float32)
    assert tr[0] == pytest.approx(1.0)
    assert tr[1] == pytest.approx(1.0)
