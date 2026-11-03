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
