"""Generadores de texturas procedurales (numpy puro, sin contexto GL)."""
from __future__ import annotations

import numpy as np


def make_checker(
    width: int = 256,
    height: int = 256,
    cell: int = 32,
    color_a: tuple[int, int, int, int] = (230, 230, 230, 255),
    color_b: tuple[int, int, int, int] = ( 40,  40,  50, 255),
) -> np.ndarray:
    """Devuelve una imagen RGBA (uint8) con un patrón de ajedrez."""
    if width <= 0 or height <= 0 or cell <= 0:
        raise ValueError("width, height y cell deben ser positivos.")

    img = np.zeros((height, width, 4), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            idx = ((x // cell) + (y // cell)) % 2
            img[y, x] = color_a if idx == 0 else color_b
    return img
