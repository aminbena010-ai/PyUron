"""Cámaras como nodos (heredan de Node3D → tienen transform)."""
from __future__ import annotations

import numpy as np

from pyuron.math import matrix
from pyuron.math.vector import Vector3
from pyuron.scene.node3d import Node3D


class _BaseCameraNode(Node3D):
    """Cámara base. Hereda de Node3D: tiene self.transform."""
    active: bool = True

    def view_projection(self, aspect: float) -> np.ndarray:
        raise NotImplementedError

    def world_position(self) -> Vector3:
        """Suma las posiciones de todos los Node3D ancestros."""
        pos = Vector3(0, 0, 0)
        node = self
        while node is not None:
            if isinstance(node, Node3D):
                pos = pos + node.transform.position
            node = node.parent
        return pos


class Camera2DNode(_BaseCameraNode):
    def __init__(self, name: str = "Camera2D") -> None:
        super().__init__(name)
        self.zoom = 1.0

    def view_projection(self, aspect: float) -> np.ndarray:
        proj = matrix.ortho(-aspect, aspect, -1.0, 1.0, -1.0, 1.0)
        p = self.world_position()
        view = (matrix.translate(-p.x, -p.y, -p.z)
                @ matrix.scale(self.zoom, self.zoom, 1.0))
        return proj @ view


class Camera3DNode(_BaseCameraNode):
    def __init__(self, name: str = "Camera3D") -> None:
        super().__init__(name)
        self.target = Vector3(0.0, 0.0, 0.0)
        self.up     = Vector3(0.0, 1.0, 0.0)
        self.fov    = 60.0
        self.near   = 0.1
        self.far    = 100.0

    def view_projection(self, aspect: float) -> np.ndarray:
        proj = matrix.perspective(self.fov, aspect, self.near, self.far)
        p = self.world_position()
        view = matrix.look_at(
            (p.x, p.y, p.z),
            (self.target.x, self.target.y, self.target.z),
            (self.up.x, self.up.y, self.up.z),
        )
        return proj @ view
