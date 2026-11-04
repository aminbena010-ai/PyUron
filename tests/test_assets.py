"""Tests para la gestión de recursos (Fase 2 de estabilización)."""

from pyuron.resources.assets import AssetManager


class FakeResource:
    def __init__(self, name, crash=False):
        self.name = name
        self.crash = crash
        self.disposed = False

    def dispose(self):
        if self.crash:
            raise RuntimeError(f"Fallo simulado en {self.name}")
        self.disposed = True


def test_dispose_all_cleans_everything():
    am = AssetManager()
    am._shaders[("a", "b")] = FakeResource("shader")
    am._textures["t"] = FakeResource("texture")
    am._meshes["m"] = FakeResource("mesh")

    am.dispose_all()

    assert am._shaders == {}
    assert am._textures == {}
    assert am._meshes == {}


def test_dispose_all_survives_one_failure():
    am = AssetManager()
    am._shaders[("bad", "b")] = FakeResource("bad_shader", crash=True)
    am._shaders[("ok", "b")] = FakeResource("ok_shader")
    am._textures["t"] = FakeResource("texture")

    am.dispose_all()  # No debe lanzar excepción

    assert am._shaders == {}
    assert am._textures == {}
    assert am._meshes == {}


def test_dispose_all_is_idempotent():
    am = AssetManager()
    am._shaders[("a", "b")] = FakeResource("s")

    am.dispose_all()
    am.dispose_all()  # No debe fallar la segunda vez

    assert am._shaders == {}


def test_engine_owns_assets():
    from pyuron import Engine
    e = Engine()
    assert hasattr(e, "assets")
    assert isinstance(e.assets, AssetManager)
