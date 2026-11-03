"""Textura 2D (RGBA, filtro linear, mipmaps)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pygame
from OpenGL.GL import (
    GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR,
    GL_RGBA, GL_RGBA8, GL_REPEAT,
    GL_TEXTURE0, GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glActiveTexture, glBindTexture, glDeleteTextures,
    glGenTextures, glGenerateMipmap, glTexImage2D, glTexParameteri,
)

from pyuron.graphics.procedural import make_checker


class Texture2D:
    def __init__(self) -> None:
        self.texture = glGenTextures(1)
        self.width = 0
        self.height = 0

    # ── Construcción ────────────────────────────────────────────────
    @classmethod
    def from_array(cls, image: np.ndarray) -> "Texture2D":
        """image: array (H, W, 4) uint8 RGBA."""
        if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 4:
            raise ValueError("La imagen debe ser (H, W, 4) uint8 RGBA.")

        t = cls()
        t.width = image.shape[1]
        t.height = image.shape[0]

        glBindTexture(GL_TEXTURE_2D, t.texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA8, t.width, t.height, 0,
            GL_RGBA, GL_UNSIGNED_BYTE, image.tobytes(),
        )
        # ↓↓↓ nombres correctos de OpenGL ↓↓↓
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return t

    @classmethod
    def from_file(cls, path: str | Path) -> "Texture2D":
        """Carga PNG/JPG/BMP usando pygame.image (sin dependencias extra)."""
        surface = pygame.image.load(str(path))
        data = pygame.image.tobytes(surface, "RGBA", True)  # flipped=True
        arr = np.frombuffer(data, dtype=np.uint8).reshape(
            surface.get_height(), surface.get_width(), 4,
        )
        return cls.from_array(np.ascontiguousarray(arr))

    @classmethod
    def checker(cls, **kwargs) -> "Texture2D":
        return cls.from_array(make_checker(**kwargs))

    # ── Uso ─────────────────────────────────────────────────────────
    def bind(self, unit: int = 0) -> None:
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def dispose(self) -> None:
        if self.texture:
            glDeleteTextures(1, [self.texture])
            self.texture = 0
