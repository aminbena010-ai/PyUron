import pytest

from pyuron.math import Vector3
from pyuron.physics.raycast import raycast
from pyuron.scene.physics_body import PhysicsBody3D, SphereBody3D


def _box(pos, size):
    b = PhysicsBody3D("Box")
    b.transform.position = Vector3(*pos)
    b.size = Vector3(*size)
    return b


def _sphere(pos, radius):
    s = SphereBody3D("Sphere", radius=radius)
    s.transform.position = Vector3(*pos)
    return s


def test_ray_hits_box():
    box = _box((0, 0, -5), (2, 2, 2))
    hit = raycast([box], Vector3(0, 0, 0), Vector3(0, 0, -1))
    assert hit is not None
    assert hit.distance == pytest.approx(4.0)
    assert hit.point.z == pytest.approx(-4.0)
    assert hit.normal.z == pytest.approx(1.0)


def test_ray_misses_box():
    box = _box((10, 0, -5), (2, 2, 2))
    hit = raycast([box], Vector3(0, 0, 0), Vector3(0, 0, -1))
    assert hit is None


def test_ray_hits_sphere():
    sphere = _sphere((0, 0, -5), 1.0)
    hit = raycast([sphere], Vector3(0, 0, 0), Vector3(0, 0, -1))
    assert hit is not None
    assert hit.distance == pytest.approx(4.0)


def test_ray_respects_max_dist():
    box = _box((0, 0, -5), (2, 2, 2))
    hit = raycast([box], Vector3(0, 0, 0), Vector3(0, 0, -1), max_dist=2.0)
    assert hit is None


def test_ray_returns_nearest_hit():
    near = _box((0, 0, -3), (2, 2, 2))
    far  = _box((0, 0, -10), (2, 2, 2))
    hit = raycast([far, near], Vector3(0, 0, 0), Vector3(0, 0, -1))
    assert hit is not None
    assert hit.body is near


def test_ray_ignores_body():
    box = _box((0, 0, -3), (2, 2, 2))
    hit = raycast([box], Vector3(0, 0, 0), Vector3(0, 0, -1), ignore=box)
    assert hit is None
