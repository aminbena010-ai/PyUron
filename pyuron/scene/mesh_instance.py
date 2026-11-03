"""Nodos renderizables: malla + material + transform (heredan de Node3D)."""
from __future__ import annotations

import numpy as np

from pyuron.graphics.material import Material
from pyuron.graphics.mesh import Mesh
from pyuron.math import matrix
from pyuron.scene.node3d import Node3D


class _MeshInstanceBase(Node3D):
    def __init__(self, name: str, mesh: Mesh, material: Material) -> None:
        super().__init__(name)
        self.mesh = mesh
        self.material = material

    def _local_model(self) -> np.ndarray:
        return self.transform.to_matrix()

    def _world_model(self) -> np.ndarray:
        """Acumula transforms de todos los Node3D ancestros."""
        m = matrix.identity()
        node = self
        while node is not None:
            if isinstance(node, Node3D):
                m = m @ node.transform.to_matrix()
            node = node.parent
        return m

    def render(self, renderer, view_projection: np.ndarray) -> None:
        if not self.visible:
            return
        mvp = view_projection @ self._world_model()
        self.material.apply(extra_uniforms={"u_mvp": mvp})
        self.mesh.draw()


class MeshInstance2D(_MeshInstanceBase):
    def __init__(self, mesh: Mesh, material: Material, name: str = "MeshInstance2D") -> None:
        super().__init__(name, mesh, material)


class MeshInstance3D(_MeshInstanceBase):
    def __init__(self, mesh: Mesh, material: Material, name: str = "MeshInstance3D") -> None:
        super().__init__(name, mesh, material)
