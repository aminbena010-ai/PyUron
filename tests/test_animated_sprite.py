import pytest

from pyuron.scene.animated_sprite2d import AnimatedSprite2D


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


def _anim(tex_w=128, tex_h=32, fw=32, fh=32):
    return AnimatedSprite2D(FakeTexture(tex_w, tex_h), FakeShader(), fw, fh)


def test_frame_count_from_grid():
    a = _anim(tex_w=128, tex_h=32, fw=32, fh=32)
    assert a.frames_x == 4
    assert a.frames_y == 1
    assert a.frame_count == 4


def test_uv_rect_maps_to_first_frame():
    a = _anim(tex_w=128, tex_h=32, fw=32, fh=32)
    a.current_frame = 0
    assert a.uv_rect() == (0.0, 0.0, 0.25, 1.0)


def test_uv_rect_maps_to_second_frame():
    a = _anim(tex_w=128, tex_h=32, fw=32, fh=32)
    a.current_frame = 1
    assert a.uv_rect() == (0.25, 0.0, 0.25, 1.0)


def test_update_advances_frames():
    a = _anim()
    a.fps = 10.0
    a.update(0.1)
    assert a.current_frame == 1
    a.update(0.1)
    assert a.current_frame == 2


def test_loop_wraps_around():
    a = _anim()
    a.fps = 10.0
    a.loop_mode = "loop"
    for _ in range(4):
        a.update(0.1)
    assert a.current_frame == 0


def test_once_stops_at_last_frame():
    a = _anim()
    a.fps = 10.0
    a.loop_mode = "once"
    for _ in range(10):
        a.update(0.1)
    assert a.current_frame == a.frame_count - 1
    assert a.playing is False


def test_ping_pong_bounces():
    a = _anim(tex_w=128, tex_h=32)
    a.fps = 10.0
    a.loop_mode = "ping_pong"
    frames = []
    for _ in range(8):
        a.update(0.1)
        frames.append(a.current_frame)
    # Debe visitar 1,2,3,2,1,... (no llegar a 0 tras 3 hasta rebotar)
    assert 3 in frames
    assert frames[-1] <= 3


def test_rejects_invalid_frames():
    with pytest.raises(ValueError):
        _anim(fw=0)
    with pytest.raises(ValueError):
        _anim(tex_w=16, tex_h=16, fw=32, fh=32)
