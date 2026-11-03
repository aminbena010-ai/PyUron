"""Escena: nodo raíz que renderiza el árbol con su cámara activa."""
from __future__ import annotations

import numpy as np

from pyuron.scene.camera_node import _BaseCameraNode
from pyuron.scene.mesh_instance import _MeshInstanceBase
from pyuron.scene.node import Node


class Scene(Node):
    def __init__(self, name: str = "Scene") -> None:
        super().__init__(name)
        self.background_color: tuple[float, float, float, float] | None = None

    def find_active_camera(self) -> _BaseCameraNode | None:
        for node in self._iter_tree():
            if isinstance(node, _BaseCameraNode) and node.active:
                return node
        return None

    def _iter_tree(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def render(self, renderer) -> None:
        camera = self.find_active_camera()
        if camera is None:
            return
        aspect = renderer.width / renderer.height
        vp = camera.view_projection(aspect)

        # Draw de todos los nodos renderizables del árbol.
        for node in self._iter_tree():
            if isinstance(node, _MeshInstanceBase):
                node.render(renderer, vp)
