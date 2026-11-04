"""Caja Alineada a los Ejes (AABB) para colisiones."""
from __future__ import annotations

from pyuron.math.vector import Vector3


class AABB:
    """Caja definida por dos esquinas: min (esquina inferior) y max (superior)."""

    __slots__ = ("min", "max")

    def __init__(self, min_v: Vector3, max_v: Vector3) -> None:
        self.min = min_v
        self.max = max_v

    @classmethod
    def from_center_size(cls, center: Vector3, size: Vector3) -> "AABB":
        half = size * 0.5
        return cls(center - half, center + half)

    def center(self) -> Vector3:
        return (self.min + self.max) * 0.5

    def size(self) -> Vector3:
        return self.max - self.min

    def intersects(self, other: "AABB") -> bool:
        return (
            self.min.x <= other.max.x and self.max.x >= other.min.x and
            self.min.y <= other.max.y and self.max.y >= other.min.y and
            self.min.z <= other.max.z and self.max.z >= other.min.z
        )

    def overlap(self, other: "AABB") -> Vector3 | None:
        """Devuelve el vector de solapamiento (siempre positivo) o None."""
        ox = min(self.max.x, other.max.x) - max(self.min.x, other.min.x)
        oy = min(self.max.y, other.max.y) - max(self.min.y, other.min.y)
        oz = min(self.max.z, other.max.z) - max(self.min.z, other.min.z)
        if ox <= 0 or oy <= 0 or oz <= 0:
            return None
        return Vector3(ox, oy, oz)

    def __repr__(self) -> str:
        return f"AABB(min={self.min}, max={self.max})"
