"""Luces como nodos: direccional (sol) y puntual (bombilla)."""
from __future__ import annotations

from pyuron.math.vector import Vector3
from pyuron.scene.node3d import Node3D


class DirectionalLightNode(Node3D):
    def __init__(self, name: str = "DirectionalLight") -> None:
        super().__init__(name)
        # La luz "apunta" en la dirección del transform.rotation
        self.rotation = Vector3(-45.0, -45.0, 0.0)
        self.color = Vector3(1.0, 0.98, 0.92)
        self.intensity = 1.0

    def direction(self) -> Vector3:
        # Rotación Euler → vector unitario (más simple: apuntar a -Z rotado)
        import numpy as np
        rx = np.radians(self.transform.rotation.x)
        ry = np.radians(self.transform.rotation.y)
        dz = -np.cos(rx) * np.cos(ry)
        dx =  np.cos(rx) * np.sin(ry)
        dy =  np.sin(rx)
        return Vector3(float(dx), float(dy), float(dz))


class PointLightNode(Node3D):
    def __init__(self, name: str = "PointLight") -> None:
        super().__init__(name)
        self.color = Vector3(1.0, 0.9, 0.7)
        self.intensity = 1.0
        self.attenuation = (1.0, 0.09, 0.032)  # (constant, linear, quadratic)
