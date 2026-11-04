"""Ciclo de vida del Engine sin ventana ni contexto OpenGL real."""
import pytest

import pyuron.core.engine as engine_module
from pyuron.core.config import EngineConfig
from pyuron.core.engine import Engine


class FakeWindow:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.closed = False
        FakeWindow.instances.append(self)

    def close(self):
        self.closed = True

    def swap_buffers(self):
        pass

    def set_size(self, w, h):
        self.size = (w, h)


class FakeRenderer:
    instances = []
    fail = False

    def __init__(self, *args, **kwargs):
        if FakeRenderer.fail:
            raise RuntimeError("sin contexto GL")
        self.version = "fake"
        FakeRenderer.instances.append(self)

    def begin_frame(self):
        pass

    def end_frame(self):
        pass

    def resize(self, w, h):
        pass


class FakeAudio:
    instances = []

    def __init__(self):
        self.init_calls = 0
        self.shutdown_calls = 0
        FakeAudio.instances.append(self)

    def init(self):
        self.init_calls += 1
        return True

    def shutdown(self):
        self.shutdown_calls += 1


@pytest.fixture
def fakes(monkeypatch):
    FakeWindow.instances = []
    FakeRenderer.instances = []
    FakeRenderer.fail = False
    FakeAudio.instances = []
    monkeypatch.setattr(engine_module, "Window", FakeWindow)
    monkeypatch.setattr(engine_module, "Renderer", FakeRenderer)
    monkeypatch.setattr(engine_module, "AudioManager", FakeAudio)
    yield


def test_initialize_and_shutdown(fakes):
    engine = Engine(EngineConfig(width=320, height=200))
    engine.initialize()

    assert isinstance(engine.window, FakeWindow)
    assert isinstance(engine.renderer, FakeRenderer)
    assert engine.audio.init_calls == 1


def test_shutdown_is_idempotent(fakes, monkeypatch):
    quit_calls = []
    monkeypatch.setattr(engine_module.pygame, "quit", lambda: quit_calls.append(1))

    engine = Engine()
    engine.initialize()
    window = engine.window
    engine.shutdown()
    engine.shutdown()

    assert window.closed is True
    assert engine.window is None
    assert engine.renderer is None
    assert len(quit_calls) == 1


def test_shutdown_before_initialize_does_not_touch_pygame(fakes, monkeypatch):
    quit_calls = []
    monkeypatch.setattr(engine_module.pygame, "quit", lambda: quit_calls.append(1))

    engine = Engine()
    engine.shutdown()

    assert quit_calls == []


def test_failed_initialize_rolls_back(fakes, monkeypatch):
    quit_calls = []
    monkeypatch.setattr(engine_module.pygame, "quit", lambda: quit_calls.append(1))
    FakeRenderer.fail = True

    engine = Engine()
    with pytest.raises(RuntimeError, match="sin contexto GL"):
        engine.initialize()

    assert engine.window is None
    assert engine.renderer is None
    assert FakeWindow.instances[0].closed is True
    assert len(quit_calls) == 1


def test_update_without_window(fakes):
    engine = Engine()
    received = []

    class DummyScene:
        def _process(self, dt):
            received.append(dt)

    engine.scene = DummyScene()
    engine.on_update(received.append)
    engine._update(0.25)

    assert received == [0.25, 0.25]


def test_variable_step_by_default(fakes):
    engine = Engine()
    assert engine._compute_steps(0.016) == [0.016]


def test_fixed_step_accumulates(fakes):
    engine = Engine(EngineConfig(fixed_dt=0.25))

    assert engine._compute_steps(0.6) == [0.25, 0.25]
    assert engine._accumulator == pytest.approx(0.1)
    assert engine._compute_steps(0.65) == [0.25, 0.25, 0.25]
    assert engine._accumulator == pytest.approx(0.0, abs=1e-9)


def test_fixed_step_is_capped(fakes):
    engine = Engine(EngineConfig(fixed_dt=0.01))
    steps = engine._compute_steps(100.0)

    assert len(steps) == Engine.MAX_FIXED_STEPS
    assert engine._accumulator == 0.0


def test_fixed_dt_validation():
    with pytest.raises(ValueError):
        EngineConfig(fixed_dt=0.0)
    with pytest.raises(ValueError):
        EngineConfig(fixed_dt=-0.1)
