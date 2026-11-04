import numpy as np
import pytest

from pyuron.math import Vector3
from pyuron.scene.sprite2d import Sprite2D


class FakeTexture:
    def __init__(self, w, h):
        self.width, self.height = w, h
        self.texture = 0
    def bind(self, unit=0):
        pass


class FakeShader:
    def use(self): pass
    def set_int(self, n, v): pass
    def set_float(self, n, v): pass
    def set_vec3(self, *a): pass
    def set_vec4(self, *a): pass
    def set_mat4(self, *a): pass
    def set_vec3_array(self, *a): pass
    def set_float_array(self, *a): pass


def _sprite(w=64, h=32, ppu=64.0):
    return Sprite2D(FakeTexture(w, h), FakeShader(), "S")


def test_default_size_from_texture_and_ppu():
    s = _sprite(w=64, h=32, ppu=64.0)
    assert s.effective_size() == (1.0, 0.5)


def test_explicit_size_overrides():
    s = _sprite()
    s.size = (2.0, 3.0)
    assert s.effective_size() == (2.0, 3.0)


def test_model_matrix_translates_and_scales():
    s = _sprite(w=64, h=64, ppu=64.0)   # 1x1 world unit
    s.transform.position = Vector3(5.0, -2.0, 0.0)
    s.transform.scale = Vector3(2.0, 3.0, 1.0)
    m = s.model_matrix()
    # El centro (0,0) → (5, -2)
    p = m @ np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
    assert p[0] == pytest.approx(5.0)
    assert p[1] == pytest.approx(-2.0)
    # La esquina (0.5, 0.5) → (6, 0.5) por escala (1*2, 1*3)
    p2 = m @ np.array([0.5, 0.5, 0.0, 1.0], dtype=np.float32)
    assert p2[0] == pytest.approx(6.0)
    assert p2[1] == pytest.approx(-0.5)


def test_uv_rect_default_full():
    s = _sprite()
    assert s.uv_rect() == (0.0, 0.0, 1.0, 1.0)
