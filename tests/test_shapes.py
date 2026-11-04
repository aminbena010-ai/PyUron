import math
import pytest

from pyuron.math import AABB, Vector3
from pyuron.physics.shapes import BoxShape, SphereShape


def test_box_aabb_uses_center_and_scale():
    box = BoxShape(Vector3(2, 2, 2))
    aabb = box.get_aabb(Vector3(1, 1, 1), Vector3(1, 1, 1))
    assert aabb.min.x == pytest.approx(0.0)
    assert aabb.max.x == pytest.approx(2.0)


def test_sphere_aabb_uses_diameter():
    sphere = SphereShape(0.5)
    aabb = sphere.get_aabb(Vector3(0, 0, 0), Vector3(1, 1, 1))
    assert aabb.max.x == pytest.approx(0.5)
    assert aabb.min.x == pytest.approx(-0.5)


def test_sphere_effective_radius_uses_average_scale():
    sphere = SphereShape(1.0)
    assert sphere.effective_radius(Vector3(2, 2, 2)) == pytest.approx(2.0)
    assert sphere.effective_radius(Vector3(1, 2, 3)) == pytest.approx(2.0)


def test_sphere_volume_formula():
    sphere = SphereShape(2.0)
    expected = (4.0 / 3.0) * math.pi * 8.0
    assert sphere.volume() == pytest.approx(expected)


def test_sphere_rejects_invalid_radius():
    with pytest.raises(ValueError):
        SphereShape(0)
    with pytest.raises(ValueError):
        SphereShape(-1)
