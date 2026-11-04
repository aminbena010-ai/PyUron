import pytest

from pyuron.math import AABB, Vector3


def test_aabb_from_center_size():
    box = AABB.from_center_size(Vector3(1, 2, 3), Vector3(2, 4, 6))
    assert box.min.x == pytest.approx(0)
    assert box.min.y == pytest.approx(0)
    assert box.min.z == pytest.approx(0)
    assert box.max.x == pytest.approx(2)
    assert box.max.y == pytest.approx(4)
    assert box.max.z == pytest.approx(6)


def test_aabb_intersects_true():
    a = AABB.from_center_size(Vector3(0, 0, 0), Vector3(2, 2, 2))
    b = AABB.from_center_size(Vector3(1, 0, 0), Vector3(2, 2, 2))
    assert a.intersects(b)


def test_aabb_intersects_false():
    a = AABB.from_center_size(Vector3(0, 0, 0), Vector3(2, 2, 2))
    b = AABB.from_center_size(Vector3(5, 0, 0), Vector3(2, 2, 2))
    assert not a.intersects(b)


def test_aabb_overlap_minimum_axis():
    a = AABB.from_center_size(Vector3(0, 0, 0), Vector3(2, 2, 2))
    b = AABB.from_center_size(Vector3(1.5, 0, 0), Vector3(2, 2, 2))
    ov = a.overlap(b)
    assert ov is not None
    assert ov.x == pytest.approx(0.5)
    assert ov.y == pytest.approx(2.0)
    assert ov.z == pytest.approx(2.0)


def test_aabb_overlap_none_when_separated():
    a = AABB.from_center_size(Vector3(0, 0, 0), Vector3(2, 2, 2))
    b = AABB.from_center_size(Vector3(10, 0, 0), Vector3(2, 2, 2))
    assert a.overlap(b) is None
