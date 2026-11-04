import json
import tempfile
from pathlib import Path

import pytest

from pyuron.math import Vector3
from pyuron.scene.node3d import Node3D
from pyuron.scene.physics_body import PhysicsBody3D
from pyuron.scene.scene import Scene
from pyuron.scene import serialization


def test_register_and_find_type():
    class DummyNode(Node3D):
        pass
    serialization.register_node_type(DummyNode)
    assert "DummyNode" in serialization._REGISTRY


def test_scene_dict_roundtrip_transform():
    scene = Scene("Test")
    n = Node3D("Child")
    n.transform.position = Vector3(1, 2, 3)
    n.transform.scale = Vector3(2, 2, 2)
    scene.add_child(n)

    d = serialization.scene_to_dict(scene)
    assert d["scene"]["type"] == "Scene"
    assert d["scene"]["children"][0]["type"] == "Node3D"
    assert d["scene"]["children"][0]["transform"]["position"] == {"x": 1.0, "y": 2.0, "z": 3.0}


def test_save_and_load_node3d_roundtrip():
    scene = Scene("Test")
    n = Node3D("N")
    n.transform.position = Vector3(5, -2, 0)
    n.transform.rotation = Vector3(0, 90, 0)
    scene.add_child(n)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "scene.json"
        scene.save_json(path)
        assert path.exists()

        loaded = Scene.load_json(path)
        assert loaded.name == "Test"
        assert len(loaded.children) == 1
        c = loaded.children[0]
        assert c.name == "N"
        assert c.transform.position.x == pytest.approx(5.0)
        assert c.transform.rotation.y == pytest.approx(90.0)


def test_physics_body_roundtrip():
    scene = Scene("Phys")
    body = PhysicsBody3D("Box")
    body.size = Vector3(2, 3, 4)
    body.mass = 10.0
    body.restitution = 0.8
    body.is_static = False
    body.transform.position = Vector3(0, 5, 0)
    scene.add_child(body)

    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "p.json"
        scene.save_json(path)
        loaded = Scene.load_json(path)

    lbox = loaded.children[0]
    assert lbox.size.x == pytest.approx(2.0)
    assert lbox.size.y == pytest.approx(3.0)
    assert lbox.size.z == pytest.approx(4.0)
    assert lbox.mass == pytest.approx(10.0)
    assert lbox.restitution == pytest.approx(0.8)
    assert lbox.transform.position.y == pytest.approx(5.0)


def test_invalid_json_raises():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "bad.json"
        path.write_text(json.dumps({"scene": {"type": "UnknownType"}}))
        with pytest.raises(ValueError, match="no registrado"):
            Scene.load_json(path)


# ── Fase 5: Tests de robustez (corrupción, versiones, errores) ──

def test_load_corrupt_json_raises_clear_error():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "bad.json"
        p.write_text("{esto no es JSON")
        with pytest.raises(ValueError, match="JSON inválido"):
            Scene.load_json(p)


def test_load_json_without_scene_key_raises():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "no_scene.json"
        p.write_text(json.dumps({"foo": "bar"}))
        with pytest.raises(ValueError, match="falta la clave raíz 'scene'"):
            Scene.load_json(p)


def test_load_node_without_type_raises():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "no_type.json"
        p.write_text(json.dumps({"version": "1.0.2", "scene": {"name": "S", "children": [{"name": "X", "children": []}]}}))
        with pytest.raises(ValueError, match="Nodo sin clave 'type'"):
            Scene.load_json(p)


def test_load_node_without_name_raises():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "no_name.json"
        p.write_text(json.dumps({"version": "1.0.2", "scene": {"type": "Scene", "name": "S", "children": [{"type": "Node3D", "children": []}]}}))
        with pytest.raises(ValueError, match="Nodo sin clave 'name'"):
            Scene.load_json(p)


def test_load_version_mismatch_warns_but_loads(caplog):
    from pyuron.scene import Scene as Sc
    scene = Sc("Vieja")
    from pyuron.scene.node3d import Node3D
    scene.add_child(Node3D("Child"))

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "old.json"
        scene.save_json(p)
        # Manipular versión para simular archivo de versión antigua
        data = json.loads(p.read_text())
        data["version"] = "0.9.0"
        p.write_text(json.dumps(data))

        loaded = Scene.load_json(p)
        assert loaded.name == "Vieja"
        assert len(loaded.children) == 1


def test_round_trip_complex_scene():
    from pyuron.math import Vector3
    from pyuron.scene.node3d import Node3D
    from pyuron.scene.physics_body import PhysicsBody3D

    scene = Scene("Complex")
    parent = Node3D("Parent")
    parent.transform.position = Vector3(1, 2, 3)
    scene.add_child(parent)

    child = PhysicsBody3D("Child")
    child.size = Vector3(2, 2, 2)
    child.mass = 5.0
    child.restitution = 0.9
    child.transform.position = Vector3(-4, 5, -6)
    parent.add_child(child)

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "complex.json"
        scene.save_json(p)
        loaded = Scene.load_json(p)

    assert loaded.name == "Complex"
    assert len(loaded.children) == 1
    par = loaded.children[0]
    assert par.name == "Parent"
    assert par.transform.position.x == pytest.approx(1.0)
    assert len(par.children) == 1
    ch = par.children[0]
    assert ch.name == "Child"
    assert ch.mass == pytest.approx(5.0)
    assert ch.restitution == pytest.approx(0.9)
    assert ch.transform.position.z == pytest.approx(-6.0)
