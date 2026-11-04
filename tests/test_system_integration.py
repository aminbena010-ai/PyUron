"""Tests de integración entre subsistemas (Fase 6)."""
from pyuron import Engine
from pyuron.scene.node import Node
from pyuron.scene.scene import Scene


class _ContextAwareNode(Node):
    """Nodo que usa el contexto del engine en on_enter_tree."""
    def __init__(self, name):
        super().__init__(name)
        self.engine_seen = None
        self.entered = False

    def on_enter_tree(self):
        self.engine_seen = self.get_engine()
        self.entered = True


def test_scene_receives_engine_context():
    e = Engine()
    scene = Scene("Main")
    e.set_scene(scene)
    e._apply_pending_scene()

    assert scene.engine is e


def test_node_can_access_engine_via_get_engine():
    e = Engine()
    scene = Scene("Main")
    n = _ContextAwareNode("Child")
    scene.add_child(n)
    e.set_scene(scene)
    e._apply_pending_scene()

    assert n.entered is True
    assert n.engine_seen is e


def test_audio_sfx_cleared_on_scene_change(monkeypatch):
    stopped = []

    e = Engine()
    monkeypatch.setattr(e.audio, "stop_all_sfx", lambda: stopped.append(True))

    scene_a = Scene("A")
    scene_b = Scene("B")
    e.set_scene(scene_a)
    e._apply_pending_scene()
    stopped.clear()

    e.set_scene(scene_b)
    e._apply_pending_scene()

    assert len(stopped) == 1


def test_exit_called_before_enter_on_scene_change():
    order = []

    e = Engine()
    scene_a = Scene("A")
    scene_a.on_exit_tree = lambda: order.append("exit:A")
    scene_b = Scene("B")
    scene_b.on_enter_tree = lambda: order.append("enter:B")

    e.set_scene(scene_a)
    e._apply_pending_scene()
    order.clear()

    e.set_scene(scene_b)
    e._apply_pending_scene()

    assert order == ["exit:A", "enter:B"]


def test_physics_cleared_between_scenes():
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.math import Vector3

    e = Engine()
    scene_a = Scene("A")
    body = PhysicsBody3D("Body")
    body.transform.position = Vector3(0, 0, 0)
    scene_a.add_child(body)
    scene_a.physics_world.bodies = [body]

    e.set_scene(scene_a)
    e._apply_pending_scene()
    e.set_scene(Scene("B"))
    e._apply_pending_scene()

    assert scene_a.physics_world.bodies == []
    assert body._in_tree is False
