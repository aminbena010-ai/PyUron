import numpy as np
import pytest

from pyuron.math import Vector3
from pyuron.scene.camera_node import Camera2DNode


def test_view_projection_respects_aspect():
    cam = Camera2DNode()
    cam.size_y = 10.0
    vp = cam.view_projection(aspect=16 / 9)
    # Proyección de (size_y/2, 0, 0) debe ser cerca del borde superior
    p = vp @ np.array([5.0, 0.0, 0.0, 1.0], dtype=np.float32)
    # half_h = 5, half_w = 5 * 16/9 ≈ 8.89 → en NDC +5 mapea a +5/8.89 = 0.56
    assert p[0] == pytest.approx(5.0 / (5.0 * 16 / 9), abs=1e-3)


def test_camera_follow_position():
    cam = Camera2DNode()
    cam.size_y = 10.0
    cam.transform.position = Vector3(2.0, 3.0, 0.0)
    vp = cam.view_projection(aspect=1.0)
    # El punto mundo (2, 3) debe proyectar a (0, 0) en NDC
    p = vp @ np.array([2.0, 3.0, 0.0, 1.0], dtype=np.float32)
    assert p[0] == pytest.approx(0.0, abs=1e-5)
    assert p[1] == pytest.approx(0.0, abs=1e-5)


def test_zoom_halves_visible_area():
    cam = Camera2DNode()
    cam.size_y = 10.0
    cam.zoom = 2.0
    vp = cam.view_projection(aspect=1.0)
    # Punto en (2.5, 0) debe quedar en el borde superior (NDC y = +1)
    p = vp @ np.array([0.0, 2.5, 0.0, 1.0], dtype=np.float32)
    assert p[1] == pytest.approx(1.0, abs=1e-3)
