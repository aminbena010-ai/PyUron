import pytest

from pyuron.math import Vector3
from pyuron.physics.world import PhysicsWorld
from pyuron.scene.physics_body import PhysicsBody3D, SphereBody3D


def _floor():
    f = PhysicsBody3D("Floor")
    f.is_static = True
    f.size = Vector3(10, 0.5, 10)
    f.transform.position = Vector3(0, -0.25, 0)
    return f


def test_sphere_falls_and_rests_on_floor():
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=4)
    sphere = SphereBody3D("S", radius=0.5)
    sphere.transform.position = Vector3(0, 3, 0)
    sphere.restitution = 0.0
    sphere.linear_damping = 0.9

    floor = _floor()
    world.bodies = [floor, sphere]

    for _ in range(120):
        world.step(1 / 60)

    # La esfera debe haber aterrizado cerca de y = 0.5 (radio)
    assert sphere.transform.position.y == pytest.approx(0.5, abs=0.1)


def test_sphere_sphere_separates():
    world = PhysicsWorld(gravity=Vector3(0, 0, 0), substeps=2)
    a = SphereBody3D("A", radius=0.5)
    b = SphereBody3D("B", radius=0.5)
    a.transform.position = Vector3(0, 0, 0)
    b.transform.position = Vector3(0.5, 0, 0)
    world.bodies = [a, b]
    world.step(0.016)

    dist = (b.transform.position - a.transform.position).length()
    assert dist >= 1.0 - 1e-3


def test_sphere_box_collision():
    world = PhysicsWorld(gravity=Vector3(0, 0, 0), substeps=2)
    box = PhysicsBody3D("Box")
    box.is_static = True
    box.size = Vector3(2, 2, 2)
    box.transform.position = Vector3(0, 0, 0)

    sphere = SphereBody3D("S", radius=0.5)
    sphere.transform.position = Vector3(1.2, 0, 0)  # Dentro del AABB del box
    world.bodies = [box, sphere]
    world.step(0.016)

    # La esfera debe haber sido empujada fuera del box (x >= 1.5 - tolerancia)
    assert sphere.transform.position.x >= 1.45
