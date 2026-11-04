"""Cuerpo rígido con forma (box por defecto o sphere)."""
from __future__ import annotations

from pyuron.math.aabb import AABB
from pyuron.math.vector import Vector3
from pyuron.physics.shapes import BoxShape, Shape, SphereShape
from pyuron.scene.node3d import Node3D


class PhysicsBody3D(Node3D):
    def __init__(self, name: str = "PhysicsBody3D", shape: Shape | None = None) -> None:
        super().__init__(name)
        self.shape: Shape = shape or BoxShape(Vector3(1.0, 1.0, 1.0))
        self.velocity = Vector3(0.0, 0.0, 0.0)
        self.is_static = False
        self.use_gravity = True
        self.mass = 1.0
        self.restitution = 0.05
        self.linear_damping = 0.85

    # ── Compatibilidad 0.5/0.6: property `size` ─────────────────────
    @property
    def size(self) -> Vector3:
        if isinstance(self.shape, BoxShape):
            return self.shape.size
        if isinstance(self.shape, SphereShape):
            r = self.shape.radius
            return Vector3(r * 2, r * 2, r * 2)
        return Vector3(1, 1, 1)

    @size.setter
    def size(self, v: Vector3) -> None:
        self.shape = BoxShape(v)

    def get_aabb(self) -> AABB:
        return self.shape.get_aabb(self.world_position(), self.transform.scale)


class SphereBody3D(PhysicsBody3D):
    """Atajo: cuerpo con forma esférica."""

    def __init__(self, name: str = "SphereBody3D", radius: float = 0.5) -> None:
        super().__init__(name, shape=SphereShape(radius))

    @property
    def radius(self) -> float:
        return self.shape.radius  # type: ignore[union-attr]

    @radius.setter
    def radius(self, v: float) -> None:
        self.shape = SphereShape(v)
