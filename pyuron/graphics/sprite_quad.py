"""Quad compartido [-0.5, 0.5]² con UVs (0,0)-(1,1). Creado on-demand."""
from __future__ import annotations

from pyuron.graphics.mesh import Mesh

_quad: Mesh | None = None


def get_sprite_quad() -> Mesh:
    """Devuelve el VAO/VBO compartido. Requiere contexto GL activo."""
    global _quad
    if _quad is None:
        verts = [
            -0.5, -0.5,  0.0, 0.0,
             0.5, -0.5,  1.0, 0.0,
             0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.0, 1.0,
        ]
        indices = [0, 1, 2, 0, 2, 3]
        _quad = Mesh(verts, indices, layout=[(0, 2), (1, 2)])
    return _quad


def dispose_sprite_quad() -> None:
    global _quad
    if _quad is not None:
        _quad.dispose()
        _quad = None
