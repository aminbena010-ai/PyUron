"""Formas de colisión: BoxShape y SphereShape."""
from __future__ import annotations

import math
from abc import ABC, abstractmethod

from pyuron.math.aabb import AABB
from pyuron.math.vector import Vector3


class Shape(ABC):
    @abstractmethod
    def get_aabb(self, center: Vector3, scale: Vector3) -> AABB: ...

    @abstractmethod
    def volume(self) -> float: ...


class BoxShape(Shape):
    """Caja alineada a los ejes con tamaño total (no half-extents)."""
    __slots__ = ("size",)

    def __init__(self, size: Vector3 | None = None) -> None:
        self.size = size or Vector3(1.0, 1.0, 1.0)

    def get_aabb(self, center: Vector3, scale: Vector3) -> AABB:
        scaled = Vector3(
            self.size.x * scale.x,
            self.size.y * scale.y,
            self.size.z * scale.z,
        )
        return AABB.from_center_size(center, scaled)

    def volume(self) -> float:
        return self.size.x * self.size.y * self.size.z


class SphereShape(Shape):
    """Esfera con radio uniforme (usa la media de las escalas para colisión)."""
    __slots__ = ("radius",)

    def __init__(self, radius: float = 0.5) -> None:
        if radius <= 0:
            raise ValueError("El radio debe ser positivo.")
        self.radius = float(radius)

    def get_aabb(self, center: Vector3, scale: Vector3) -> AABB:
        r = self.effective_radius(scale)
        return AABB.from_center_size(center, Vector3(r * 2, r * 2, r * 2))

    def effective_radius(self, scale: Vector3) -> float:
        avg = (scale.x + scale.y + scale.z) / 3.0
        return self.radius * avg

    def volume(self) -> float:
        return (4.0 / 3.0) * math.pi * self.radius ** 3
