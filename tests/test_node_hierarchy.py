"""Invariantes y recorrido del SceneTree."""
import pytest

from pyuron.math.vector import Vector3
from pyuron.scene.camera_node import Camera2DNode
from pyuron.scene.node import Node
from pyuron.scene.node3d import Node3D


def test_add_child_sets_parent_once():
    root = Node("root")
    child = Node("child")
    root.add_child(child)

    assert child.parent is root
    assert root.children == [child]


def test_reparent_moves_child():
    a, b, child = Node("a"), Node("b"), Node("child")
    a.add_child(child)
    b.add_child(child)

    assert child.parent is b
    assert a.children == []
    assert b.children == [child]


def test_add_self_raises():
    node = Node("n")
    with pytest.raises(ValueError, match="ciclo"):
        node.add_child(node)


def test_add_ancestor_raises():
    root = Node("root")
    child = Node("child")
    root.add_child(child)

    with pytest.raises(ValueError, match="ciclo"):
        child.add_child(root)
    assert root.parent is None


def test_remove_child_returns_bool():
    root = Node("root")
    child = Node("child")
    other = Node("other")
    root.add_child(child)

    assert root.remove_child(child) is True
    assert child.parent is None
    assert root.children == []
    assert root.remove_child(other) is False
    assert other.parent is None


def test_process_is_depth_first_and_uses_snapshot():
    root = Node("root")
    a = Node("a")
    b = Node("b")
    root.add_child(a)
    root.add_child(b)
    order = []

    root.update = lambda dt: order.append("root")
    a.update = lambda dt: order.append("a")
    b.update = lambda dt: order.append("b")

    root._process(0.016)
    assert order == ["root", "a", "b"]


def test_child_added_by_sibling_waits_one_frame():
    root = Node("root")
    a = Node("a")
    root.add_child(a)
    seen = []

    def a_update(_dt):
        seen.append("a")
        if len(root.children) == 1:
            b = Node("b")
            b.update = lambda _dt: seen.append("b")
            root.add_child(b)

    a.update = a_update

    root._process(0.016)
    assert seen == ["a"]

    root._process(0.016)
    assert seen == ["a", "a", "b"]


def test_world_position_sums_ancestors():
    root = Node3D("root")
    root.transform.position = Vector3(1, 2, 3)
    child = Node3D("child")
    child.transform.position = Vector3(0, 1, 0)
    root.add_child(child)

    assert child.world_position().x == pytest.approx(1)
    assert child.world_position().y == pytest.approx(3)


def test_camera_inherits_world_position():
    root = Node3D("root")
    root.transform.position = Vector3(0, 5, 0)
    cam = Camera2DNode()
    root.add_child(cam)

    assert cam.world_position().y == pytest.approx(5)
