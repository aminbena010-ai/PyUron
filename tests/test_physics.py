import pytest

from pyuron.math import Vector3
from pyuron.physics.world import PhysicsWorld
from pyuron.scene.physics_body import PhysicsBody3D


def _body(pos=(0, 0, 0), size=(1, 1, 1), **kw):
    b = PhysicsBody3D("Test")
    b.transform.position = Vector3(*pos)
    b.size = Vector3(*size)
    for k, v in kw.items():
        setattr(b, k, v)
    return b


def test_gravity_integrates_downward():
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=1)
    body = _body(pos=(0, 100, 0))
    body.linear_damping = 1.0  # Desactivar fricción para testear solo gravedad
    world.bodies = [body]
    world.step(0.1)
    # Después de 0.1s con g=-10: v = -1 m/s, y = 100 - 0.1 = 99.9
    assert body.velocity.y == pytest.approx(-1.0)
    assert body.transform.position.y == pytest.approx(99.9)


def test_static_body_does_not_move():
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=1)
    body = _body(pos=(0, 10, 0), is_static=True)
    world.bodies = [body]
    world.step(1.0)
    assert body.transform.position.y == pytest.approx(10.0)
    assert body.velocity.y == pytest.approx(0.0)


def test_cube_bounces_on_floor():
    world = PhysicsWorld(gravity=Vector3(0, -10, 0), substeps=2)

    floor = _body(pos=(0, -0.25, 0), size=(10, 0.5, 10), is_static=True)
    cube  = _body(pos=(0, 0.4, 0), size=(1, 1, 1), restitution=0.5)
    # El cubo está 0.4 sobre 0, con su AABB inferior en -0.1 (dentro del suelo).

    world.bodies = [floor, cube]
    world.step(0.016)

    # Debe haber sido empujado fuera del suelo (arriba)
    assert cube.transform.position.y > 0.5 - 1e-3
    # Y su velocidad Y no debe seguir siendo negativa grande
    assert cube.velocity.y >= 0.0 or abs(cube.velocity.y) < 10.0


def test_two_dynamic_bodies_separate():
    world = PhysicsWorld(gravity=Vector3(0, 0, 0), substeps=1)
    a = _body(pos=(0.0, 0, 0), size=(1, 1, 1))
    b = _body(pos=(0.5, 0, 0), size=(1, 1, 1))
    world.bodies = [a, b]
    world.step(0.001)
    # Después de resolver, deben estar separados al menos 1 en X
    assert abs(b.transform.position.x - a.transform.position.x) >= 1.0 - 1e-3


def test_no_collision_when_separated():
    world = PhysicsWorld(gravity=Vector3(0, 0, 0), substeps=1)
    a = _body(pos=(0, 0, 0), size=(1, 1, 1))
    b = _body(pos=(5, 0, 0), size=(1, 1, 1))
    world.bodies = [a, b]
    world.step(0.1)
    assert a.transform.position.x == pytest.approx(0.0)
    assert b.transform.position.x == pytest.approx(5.0)
