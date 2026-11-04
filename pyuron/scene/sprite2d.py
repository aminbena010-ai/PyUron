"""Sprite 2D: quad texturizado con tint, flip y tamaño en unidades de mundo."""
from __future__ import annotations

import numpy as np

from enum import Enum

from pyuron.graphics.material import Material
from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.math import matrix
from pyuron.scene.node2d import Node2D


class Anchor(Enum):
    CENTER = (0.0, 0.0)
    TOP_LEFT = (-0.5, 0.5)
    TOP_RIGHT = (0.5, 0.5)
    BOTTOM_LEFT = (-0.5, -0.5)
    BOTTOM_RIGHT = (0.5, -0.5)
    TOP_CENTER = (0.0, 0.5)
    BOTTOM_CENTER = (0.0, -0.5)
    LEFT_CENTER = (-0.5, 0.0)
    RIGHT_CENTER = (0.5, 0.0)


class Sprite2D(Node2D):
    def __init__(self, texture: Texture2D, shader: Shader, name: str = "Sprite2D") -> None:
        super().__init__(name)
        self.texture = texture
        self.material = Material(
            shader=shader,
            uniforms={},
            textures={"u_texture": texture},
        )
        # size=None → derivado de textura / ppu
        self.size: tuple[float, float] | None = None
        self.ppu: float = 64.0
        self.tint: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
        self.flip_x: bool = False
        self.flip_y: bool = False
        self.z_index: int = 0
        self.anchor: Anchor = Anchor.CENTER

    # ── Cálculos puros (testeables sin GL) ──────────────────────────
    def effective_size(self) -> tuple[float, float]:
        if self.size is not None:
            return self.size
        return (self.texture.width / self.ppu, self.texture.height / self.ppu)

    def model_matrix(self) -> np.ndarray:
        t = self.transform
        s = self.effective_size()
        m = matrix.identity()
        m = m @ matrix.translate(t.position.x, t.position.y, t.position.z)
        m = m @ matrix.rotate_z(t.rotation.z)
        m = m @ matrix.scale(s[0] * t.scale.x, s[1] * t.scale.y, 1.0)
        return m

    def world_model(self) -> np.ndarray:
        """Acumula transforms de todos los ancestros con `.transform`."""
        chain = []
        node = self
        while node is not None:
            if hasattr(node, "transform"):
                chain.append(node)
            node = node.parent
        chain.reverse()
        m = matrix.identity()
        for n in chain:
            m = m @ n.transform.to_matrix()
        return m

    def uv_rect(self) -> tuple[float, float, float, float]:
        return (0.0, 0.0, 1.0, 1.0)

    # ── Render ──────────────────────────────────────────────────────
    def render(self, renderer, view_projection: np.ndarray) -> None:
        if not self.visible:
            return
        from pyuron.graphics.sprite_quad import get_sprite_quad

        # Aplicar el tamaño real del sprite y el anclaje
        w, h = self.effective_size()
        ax, ay = self.anchor.value
        anchor_offset = matrix.translate(ax * w, ay * h, 0.0)
        size_matrix = matrix.scale(w, h, 1.0)
        mvp = view_projection @ self.world_model() @ anchor_offset @ size_matrix
        uniforms = {
            "u_mvp":    mvp,
            "u_uv_rect": self.uv_rect(),
            "u_tint":    self.tint,
            "u_flip_x": -1.0 if self.flip_x else 1.0,
            "u_flip_y": -1.0 if self.flip_y else 1.0,
        }
        self.material.apply(extra_uniforms=uniforms)
        get_sprite_quad().draw()
