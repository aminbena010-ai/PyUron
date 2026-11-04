"""Tests del ciclo de vida de escenas y nodos (Fase 4)."""
from pyuron.scene.node import Node
from pyuron.scene.scene import Scene


class _TrackingNode(Node):
    """Nodo que registra cuándo entra/sale del árbol."""
    def __init__(self, name, log):
        super().__init__(name)
        self.log = log

    def on_enter_tree(self):
        self.log.append(f"enter:{self.name}")

    def on_exit_tree(self):
        self.log.append(f"exit:{self.name}")


# ── Ciclo de vida de nodos ──────────────────────────────────────

def test_add_child_to_active_tree_triggers_enter():
    scene = Scene("S")
    log = []
    scene._enter_tree_recursive()
    n = _TrackingNode("N", log)
    scene.add_child(n)
    assert "enter:N" in log


def test_add_child_to_inactive_tree_does_not_trigger_enter():
    scene = Scene("S")  # NO _enter_tree_recursive
    log = []
    n = _TrackingNode("N", log)
    scene.add_child(n)
    assert log == []


def test_remove_child_triggers_exit():
    scene = Scene("S")
    log = []
    n = _TrackingNode("N", log)
    scene.add_child(n)
    scene._enter_tree_recursive()
    log.clear()

    scene.remove_child(n)
    assert "exit:N" in log


def test_enter_propagates_to_children():
    scene = Scene("S")
    log = []
    parent = _TrackingNode("P", log)
    child = _TrackingNode("C", log)
    parent.add_child(child)
    scene.add_child(parent)

    scene._enter_tree_recursive()
    assert "enter:P" in log
    assert "enter:C" in log


def test_exit_propagates_to_children():
    scene = Scene("S")
    log = []
    parent = _TrackingNode("P", log)
    child = _TrackingNode("C", log)
    parent.add_child(child)
    scene.add_child(parent)
    scene._enter_tree_recursive()
    log.clear()

    scene._exit_tree_recursive()
    assert "exit:C" in log
    assert "exit:P" in log


def test_exit_after_enter_called_once():
    scene = Scene("S")
    log = []
    n = _TrackingNode("N", log)
    scene.add_child(n)
    scene._enter_tree_recursive()
    scene._exit_tree_recursive()
    scene._exit_tree_recursive()  # doble exit → no duplica

    assert log.count("exit:N") == 1


# ── Limpieza de física en Scene ─────────────────────────────────

def test_scene_exit_clears_physics():
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.math import Vector3
    scene = Scene("S")
    body = PhysicsBody3D("Body")
    body.transform.position = Vector3(0, 0, 0)
    scene.add_child(body)
    scene.physics_world.bodies = [body]

    scene._enter_tree_recursive()
    scene._exit_tree_recursive()

    assert scene.physics_world.bodies == []


# ── Cola de escenas del Engine ──────────────────────────────────

def test_engine_set_scene_queues_until_apply(monkeypatch):
    from pyuron import Engine

    e = Engine()
    scene1 = Scene("One")
    scene2 = Scene("Two")

    e.set_scene(scene1)
    assert e.scene is None
    assert e._pending_scene is scene1

    e._apply_pending_scene()
    assert e.scene is scene1
    assert e._pending_scene is None

    e.set_scene(scene2)
    assert e.scene is scene1
    assert e._pending_scene is scene2

    e._apply_pending_scene()
    assert e.scene is scene2


def test_engine_scene_change_calls_exit_and_enter():
    from pyuron import Engine

    e = Engine()
    log = []
    scene1 = Scene("One")
    scene1.on_exit_tree = lambda: log.append("exit:One")
    scene2 = Scene("Two")
    scene2.on_enter_tree = lambda: log.append("enter:Two")

    e.set_scene(scene1)
    e._apply_pending_scene()

    e.set_scene(scene2)
    e._apply_pending_scene()

    assert "exit:One" in log
    assert "enter:Two" in log


def test_engine_set_scene_inside_update_is_safe():
    """Simula un nodo que cambia de escena dentro de update."""
    from pyuron import Engine

    e = Engine()
    scene_a = Scene("A")
    scene_b = Scene("B")

    e.set_scene(scene_a)
    e._apply_pending_scene()

    # Nodo de A que cambia de escena en su update
    class SwitchNode(Node):
        def update(self, dt):
            e.set_scene(scene_b)

    switcher = SwitchNode("Switcher")
    scene_a.add_child(switcher)

    # Simulamos un frame completo
    e._update(0.016)
    # Después de update, la escena pendiente NO se ha aplicado todavía
    assert e.scene is scene_a
    assert e._pending_scene is scene_b

    e._apply_pending_scene()
    assert e.scene is scene_b
