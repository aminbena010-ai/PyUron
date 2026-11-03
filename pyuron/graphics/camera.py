"""Cámaras 2D ortográfica y 3D perspectiva."""
from __future__ import annotations

import numpy as np

from pyuron.math import matrix
from pyuron.math.vector import Vector3


class Camera2D:
    def __init__(self, width: int, height: int) -> None:
        self.position = Vector3(0.0, 0.0, 0.0)
        self.zoom = 1.0
        self.projection = np.eye(4, dtype=np.float32)
        self.set_viewport(width, height)

    def set_viewport(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)
        aspect = self.width / self.height
        # X visible: [-aspect, aspect] · Y visible: [-1, 1]
        self.projection = matrix.ortho(-aspect, aspect, -1.0, 1.0, -1.0, 1.0)

    def view(self) -> np.ndarray:
        v = matrix.translate(-self.position.x, -self.position.y, -self.position.z)
        return v @ matrix.scale(self.zoom, self.zoom, 1.0)

    def view_projection(self) -> np.ndarray:
        return self.projection @ self.view()


class Camera3D:
    def __init__(self, width: int, height: int) -> None:
        self.position = Vector3(0.0, 0.0, 3.0)
        self.target   = Vector3(0.0, 0.0, 0.0)
        self.up       = Vector3(0.0, 1.0, 0.0)
        self.fov      = 60.0
        self.near     = 0.1
        self.far      = 100.0
        self.projection = np.eye(4, dtype=np.float32)
        self.set_viewport(width, height)

    def set_viewport(self, width: int, height: int) -> None:
        aspect = max(1, width) / max(1, height)
        self.projection = matrix.perspective(self.fov, aspect, self.near, self.far)

    def view(self) -> np.ndarray:
        return matrix.look_at(
            (self.position.x, self.position.y, self.position.z),
            (self.target.x,   self.target.y,   self.target.z),
            (self.up.x,       self.up.y,       self.up.z),
        )

    def view_projection(self) -> np.ndarray:
        return self.projection @ self.view()
