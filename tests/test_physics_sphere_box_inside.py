"""Regresión: esfera con el centro dentro de una caja estática.

El centro de la esfera coincide con el punto más cercano de la caja, por lo
que la resolución usa la rama de penetración profunda. Debe expulsar la esfera
por la cara más cercana, con la profundidad correcta y el signo correcto.
"""
import pytest

from pyuron.math.vector import Vector3
from pyuron.physics.world import PhysicsWorld
from pyuron.scene.physics_body import PhysicsBody3D, SphereBody3D


def _world():
    return PhysicsWorld(gravity=Vector3(0, 0, 0), substeps=1)


def _box(size=(1.0, 1.0, 1.0)):
    box = PhysicsBody3D("Box")
    box.size = Vector3(*size)
    box.is_static = True
    return box


def _sphere(position, radius=0.2):
    sphere = SphereBody3D("Sphere", radius=radius)
    sphere.transform.position = Vector3(*position)
    sphere.use_gravity = False
    sphere.linear_damping = 1.0
    sphere.restitution = 0.0
    return sphere


def _step(world, box, sphere):
    world.bodies = [box, sphere]
    world.step(1 / 60)


def test_inside_pushes_along_negative_y():
    world, box = _world(), _box()
    sphere = _sphere((0.3, -0.4, 0.0))
    _step(world, box, sphere)

    assert sphere.transform.position.y == pytest.approx(-0.7, abs=1e-4)
    assert sphere.transform.position.x == pytest.approx(0.3, abs=1e-4)
    assert sphere.transform.position.z == pytest.approx(0.0, abs=1e-4)


def test_inside_pushes_along_negative_x_with_correct_depth():
    world, box = _world(), _box()
    sphere = _sphere((-0.42, 0.1, 0.0))
    _step(world, box, sphere)

    assert sphere.transform.position.x == pytest.approx(-0.7, abs=1e-4)
    assert sphere.transform.position.y == pytest.approx(0.1, abs=1e-4)


def test_inside_pushes_along_negative_z_not_x():
    world, box = _world(), _box()
    sphere = _sphere((0.3, 0.2, -0.42))
    _step(world, box, sphere)

    assert sphere.transform.position.z == pytest.approx(-0.7, abs=1e-4)
    assert sphere.transform.position.x == pytest.approx(0.3, abs=1e-4)


def test_inside_pushes_towards_nearest_face():
    world, box = _world(), _box()
    sphere = _sphere((0.0, 0.0, 0.0), radius=0.1)
    _step(world, box, sphere)

    moved = (
        abs(sphere.transform.position.x)
        + abs(sphere.transform.position.y)
        + abs(sphere.transform.position.z)
    )
    assert moved == pytest.approx(0.6, abs=1e-4)


def test_static_static_does_not_move():
    world = _world()
    box_a, box_b = _box(), _box()
    box_b.is_static = True
    box_b.transform.position = Vector3(0.0, 0.4, 0.0)
    world.bodies = [box_a, box_b]
    world.step(1 / 60)

    assert box_b.transform.position.y == pytest.approx(0.4)
