from pyuron.scene.label_node import render_text_surface, surface_to_array


def test_render_returns_surface():
    surf = render_text_surface("Hola PyUron", font_size=24)
    assert surf.get_width() > 0
    assert surf.get_height() > 0


def test_surface_to_array_shape():
    surf = render_text_surface("X", font_size=32)
    arr = surface_to_array(surf)
    assert arr.ndim == 3
    assert arr.shape[2] == 4
    assert arr.shape[0] == surf.get_height()
    assert arr.shape[1] == surf.get_width()


def test_longer_text_wider_surface():
    s1 = render_text_surface("A", font_size=24)
    s2 = render_text_surface("AAAAAAAA", font_size=24)
    assert s2.get_width() > s1.get_width()


def test_bigger_font_taller_surface():
    s1 = render_text_surface("A", font_size=12)
    s2 = render_text_surface("A", font_size=48)
    assert s2.get_height() > s1.get_height()
