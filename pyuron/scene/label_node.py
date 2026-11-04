"""LabelNode: texto renderizado a textura, dibujado como sprite."""
from __future__ import annotations

import numpy as np
import pygame

from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.scene.sprite2d import Sprite2D


def render_text_surface(
    text: str,
    font_size: int = 24,
    color: tuple[int, int, int, int] = (255, 255, 255, 255),
) -> pygame.Surface:
    """Renderiza texto a un Surface RGBA. Pure: sin GL."""
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.Font(None, font_size)
    return font.render(text, True, color)


def surface_to_array(surface: pygame.Surface) -> np.ndarray:
    """Convierte Surface → ndarray (H, W, 4) uint8."""
    data = pygame.image.tobytes(surface, "RGBA", True)
    arr = np.frombuffer(data, dtype=np.uint8).reshape(
        surface.get_height(), surface.get_width(), 4,
    )
    return np.ascontiguousarray(arr)


class LabelNode(Sprite2D):
    """Sprite cuyo contenido es texto. Regenera textura al cambiar texto/fuente/color."""

    def __init__(
        self,
        text: str,
        font_size: int,
        shader: Shader,
        color: tuple[int, int, int, int] = (255, 255, 255, 255),
        name: str = "Label",
    ) -> None:
        self.text = text
        self.font_size = font_size
        self.color = color

        surface = render_text_surface(text, font_size, color)
        texture = Texture2D.from_array(surface_to_array(surface))
        super().__init__(texture, shader, name)

        # Tamaño en unidades: 1 px = 1/ppu unidades (default 32)
        self.ppu = 32.0

    # ── API ────────────────────────────────────────────────────────
    def set_text(self, text: str) -> None:
        if text == self.text:
            return
        self.text = text
        self._rebuild_texture()

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        if color == self.color:
            return
        self.color = color
        self._rebuild_texture()

    def set_font_size(self, size: int) -> None:
        if size == self.font_size:
            return
        self.font_size = size
        self._rebuild_texture()

    def _rebuild_texture(self) -> None:
        surface = render_text_surface(self.text, self.font_size, self.color)
        arr = surface_to_array(surface)
        old = self.texture
        self.texture = Texture2D.from_array(arr)
        self.material.textures["u_texture"] = self.texture
        if old is not None:
            old.dispose()
        # Resetear `size` para que se derive del nuevo tamaño de la textura
        self.size = None
