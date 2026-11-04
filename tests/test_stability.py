"""Tests de estabilidad y estrés (Fase 7 — Estabilización 1.0.2).

Estos tests NO buscan nuevas funcionalidades. Buscan que el motor se
comporte de forma predecible bajo:
  - Árboles muy profundos o anchos
  - Añadir/eliminar muchos nodos en un frame
  - dt extremos (enorme, diminuto, cero)
  - Física caótica con muchos cuerpos o velocidades altas
  - Serialización repetida (round-trip 10x)
  - Creación/destrucción repetida del motor
"""
import math
import random
import tempfile
import time
from pathlib import Path

import pytest

from pyuron import Engine, EngineConfig, Vector3
from pyuron.physics.world import PhysicsWorld
from pyuron.scene.node import Node
from pyuron.scene.node3d import Node3D
from pyuron.scene.physics_body import PhysicsBody3D
from pyuron.scene.scene import Scene


# ══════════════════════════════════════════════════════════════
#  Árbol de nodos — profundidad, anchura, ciclos
# ══════════════════════════════════════════════════════════════

def test_deep_tree_100_levels_no_stack_overflow():
    """Cadena de 100 niveles — no debe haber RecursionError."""
    root = Node("Root")
    current = root
    for i in range(100):
        child = Node(f"N{i}")
        current.add_child(child)
        current = child
    assert current.parent is not None


def test_wide_tree_100_siblings():
    root = Node("Root")
    for i in range(100):
        root.add_child(Node(f"S{i}"))
    assert len(root.children) == 100


def test_add_remove_500_nodes_no_leak():
    """Añadir y quitar 500 nodos → árbol vacío al final, sin fugas."""
    scene = Scene("S")
    scene._enter_tree_recursive()
    for i in range(500):
        n = Node(f"N{i}")
        scene.add_child(n)
        scene.remove_child(n)
    assert len(scene.children) == 0


def test_get_engine_walks_up_50_level_chain():
    """En cadena profunda, get_engine sigue encontrando la escena."""
    scene = Scene("S")
    scene.engine = "fake_engine"
    scene._enter_tree_recursive()
    current = scene
    for i in range(50):
        child = Node(f"N{i}")
        current.add_child(child)
        current = child
    assert current.get_engine() == "fake_engine"


def test_cycle_prevented_in_deep_chain():
    """Un nodo al final de una cadena de 50 no puede apuntar a la raíz."""
    root = Node("Root")
    current = root
    for i in range(50):
        child = Node(f"N{i}")
        current.add_child(child)
        current = child
    with pytest.raises(ValueError, match="ciclo"):
        current.add_child(root)


def test_adding_500_nodes_is_fast():
    """Añadir 500 nodos debe tardar < 2 s (detecta O(N²) accidentales)."""
    start = time.perf_counter()
    root = Node("Root")
    for i in range(500):
        root.add_child(Node(f"N{i}"))
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"Añadir 500 nodos tardó {elapsed:.2f}s"


# ══════════════════════════════════════════════════════════════
#  Sistema de tiempo — dt extremos
# ══════════════════════════════════════════════════════════════

def test_compute_steps_with_huge_dt_caps():
    """dt = 100 s → se limita a MAX_FIXED_STEPS, no intenta 6000 pasos."""
    e = Engine(EngineConfig(fixed_dt=0.016))
    steps = e._compute_steps(100.0)
    assert len(steps) == Engine.MAX_FIXED_STEPS
    assert e._accumulator == 0.0


def test_compute_steps_with_tiny_dt_accumulates():
    """Dos pasos de 0.05 s = 1 paso de fixed_dt=0.1 s."""
    e = Engine(EngineConfig(fixed_dt=0.1))
    total = 0
    total += len(e._compute_steps(0.05))
    total += len(e._compute_steps(0.05))
    assert total == 1


def test_compute_steps_handles_zero_dt():
    """dt = 0 no debe producir pasos ni romper el acumulador."""
    e = Engine(EngineConfig(fixed_dt=0.016))
    steps = e._compute_steps(0.0)
    assert steps == []
    assert e._accumulator == 0.0


def test_compute_steps_1000_random_frames_stable():
    """1000 frames con dt aleatorio → acumulador siempre en [0, fixed_dt]."""
    e = Engine(EngineConfig(fixed_dt=0.016))
    rng = random.Random(42)
    for _ in range(1000):
        dt = rng.uniform(0.001, 0.05)
        steps = e._compute_steps(dt)
        # El acumulador nunca debe desbordar (con margen por float)
        assert e._accumulator >= -1e-9
        assert e._accumulator <= e.fixed_dt + 1e-9
        # Los pasos son siempre del tamaño fijo
        assert all(s == e.fixed_dt for s in steps)


# ══════════════════════════════════════════════════════════════
#  Física — muchos cuerpos y velocidades extremas
# ══════════════════════════════════════════════════════════════

def test_physics_20_bodies_no_nan():
    """20 cuerpos cayendo 2 s → ninguno produce NaN ni Inf."""
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=2)
    floor = PhysicsBody3D("Floor")
    floor.is_static = True
    floor.size = Vector3(100, 0.5, 100)
    floor.transform.position = Vector3(0, -0.25, 0)
    bodies = [floor]
    for i in range(20):
        b = PhysicsBody3D(f"B{i}")
        b.size = Vector3(1, 1, 1)
        x = (i % 5) * 3 - 6
        z = (i // 5) * 3 - 6
        b.transform.position = Vector3(x, 5 + i // 5, z)
        bodies.append(b)
    world.bodies = bodies

    for _ in range(120):  # 2 s a 60 FPS
        world.step(1 / 60)

    for b in bodies:
        p = b.transform.position
        assert not math.isnan(p.x)
        assert not math.isnan(p.y)
        assert not math.isnan(p.z)
        assert not math.isinf(p.x)
        assert not math.isinf(p.y)
        assert not math.isinf(p.z)


def test_physics_extreme_velocity_does_not_tunnel():
    """Velocidad -50 m/s con substeps=4 → no atraviesa el suelo."""
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=4)
    floor = PhysicsBody3D("Floor")
    floor.is_static = True
    floor.size = Vector3(10, 0.5, 10)
    floor.transform.position = Vector3(0, -0.25, 0)

    fast = PhysicsBody3D("Fast")
    fast.size = Vector3(0.5, 0.5, 0.5)
    fast.transform.position = Vector3(0, 5, 0)
    fast.velocity = Vector3(0, -50, 0)
    fast.restitution = 0.0
    fast.linear_damping = 1.0

    world.bodies = [floor, fast]
    for _ in range(60):
        world.step(1 / 60)

    # Debe haberse detenido en o sobre el suelo
    assert fast.transform.position.y > -0.5
    # Y no debería estar a años luz por encima
    assert fast.transform.position.y < 2.0


# ══════════════════════════════════════════════════════════════
#  Serialización — round-trip repetido y casos extremos
# ══════════════════════════════════════════════════════════════

def test_serialization_roundtrip_10_times_is_stable():
    """Guardar + cargar 10 veces consecutivas debe dar el mismo JSON."""
    scene = Scene("Original")
    for i in range(5):
        n = Node3D(f"N{i}")
        n.transform.position = Vector3(i, i * 2, i * 3)
        scene.add_child(n)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "s.json"
        scene.save_json(p)

        previous = None
        for _ in range(10):
            loaded = Scene.load_json(p)
            loaded.save_json(p)
            current = p.read_text()
            if previous is not None:
                assert current == previous
            previous = current


def test_empty_scene_roundtrip():
    scene = Scene("Empty")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "e.json"
        scene.save_json(p)
        loaded = Scene.load_json(p)
    assert loaded.name == "Empty"
    assert len(loaded.children) == 0


def test_unicode_names_roundtrip():
    scene = Scene("Ñandú")
    n = Node3D("Niño")
    scene.add_child(n)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "u.json"
        scene.save_json(p)
        loaded = Scene.load_json(p)
    assert loaded.name == "Ñandú"
    assert loaded.children[0].name == "Niño"


# ══════════════════════════════════════════════════════════════
#  Ciclo de vida — crear y destruir el motor repetidamente
# ══════════════════════════════════════════════════════════════

def test_repeated_engine_creation_and_shutdown():
    """Crear y destruir 3 engines seguidos no debe romper nada."""
    for i in range(3):
        e = Engine(EngineConfig(title=f"Test {i}"))
        e.shutdown()           # sin initialize
        assert e._closed is True
        e.shutdown()           # segunda → no-op
        assert e._closed is True


def test_engine_shutdown_twice_no_error():
    e = Engine()
    e.shutdown()
    e.shutdown()  # no debe lanzar
    assert e._closed is True


def test_engine_can_be_recreated_after_shutdown():
    """Un Engine cerrado no impide crear otro nuevo."""
    e1 = Engine()
    e1.shutdown()
    e2 = Engine()
    assert e2._closed is False
    assert e2.scene is None
    e2.shutdown()


# ══════════════════════════════════════════════════════════════
#  Escenas — cambios rápidos
# ══════════════════════════════════════════════════════════════

def test_rapid_scene_changes_100_times():
    """Cambiar de escena 100 veces rápido → sin crash ni fugas."""
    e = Engine()
    for i in range(100):
        e.set_scene(Scene(f"S{i}"))
        e._apply_pending_scene()
    assert e.scene is not None
    assert e.scene.name == "S99"


def test_scene_with_many_children_change_cleanly():
    """Escena con 50 hijos → cambio a otra → se limpia bien."""
    e = Engine()
    scene_a = Scene("A")
    for i in range(50):
        scene_a.add_child(Node(f"N{i}"))
    e.set_scene(scene_a)
    e._apply_pending_scene()

    scene_b = Scene("B")
    e.set_scene(scene_b)
    e._apply_pending_scene()

    assert len(scene_a.children) == 50  # intacta, pero fuera del árbol
    assert e.scene is scene_b
    # Ningún nodo de A debe estar en el árbol activo
    for n in scene_a.children:
        assert n._in_tree is False
