"""Transformación 3D: posición, rotación (Euler XYZ), escala."""
from __future__ import annotations

import numpy as np

from pyuron.math import matrix
from pyuron.math.vector import Vector3


class Transform:
    def __init__(self) -> None:
        self.position = Vector3(0.0, 0.0, 0.0)
        self.rotation = Vector3(0.0, 0.0, 0.0)
        self.scale    = Vector3(1.0, 1.0, 1.0)

    def to_matrix(self) -> np.ndarray:
        m = matrix.identity()
        m = m @ matrix.translate(self.position.x, self.position.y, self.position.z)
        m = m @ matrix.rotate_z(self.rotation.z)
        m = m @ matrix.rotate_y(self.rotation.y)
        m = m @ matrix.rotate_x(self.rotation.x)
        m = m @ matrix.scale(self.scale.x, self.scale.y, self.scale.z)
        return m

    def to_dict(self) -> dict:
        return {
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "scale":    self.scale.to_dict(),
        }

    def load_dict(self, d: dict) -> None:
        if "position" in d:
            self.position = Vector3.from_dict(d["position"])
        if "rotation" in d:
            self.rotation = Vector3.from_dict(d["rotation"])
        if "scale" in d:
            self.scale = Vector3.from_dict(d["scale"])
