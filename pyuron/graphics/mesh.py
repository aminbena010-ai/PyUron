"""Malla con VAO + VBO + EBO."""
from __future__ import annotations

import ctypes

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER, GL_FALSE, GL_FLOAT,
    GL_STATIC_DRAW, GL_TRIANGLES, GL_UNSIGNED_INT,
    glBindBuffer, glBindVertexArray, glBufferData, glDeleteBuffers,
    glDeleteVertexArrays, glDrawElements, glEnableVertexAttribArray,
    glGenBuffers, glGenVertexArrays, glVertexAttribPointer,
)


class Mesh:
    """Malla indexada. El layout por defecto es (pos3, color3)."""

    def __init__(
        self,
        vertices: list | np.ndarray,
        indices: list[int] | np.ndarray,
        layout: list[tuple[int, int]] | None = None,
    ) -> None:
        self._layout = layout or [(0, 3), (1, 3)]
        self._index_count = len(indices)

        verts = np.asarray(vertices, dtype=np.float32).flatten()
        inds  = np.asarray(indices, dtype=np.uint32).flatten()

        self._vao = glGenVertexArrays(1)
        self._vbo = glGenBuffers(1)
        self._ebo = glGenBuffers(1)

        glBindVertexArray(self._vao)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, inds.nbytes, inds, GL_STATIC_DRAW)

        stride = sum(n for _, n in self._layout) * 4
        offset = 0
        for attr_index, comps in self._layout:
            glEnableVertexAttribArray(attr_index)
            glVertexAttribPointer(
                attr_index, comps, GL_FLOAT, GL_FALSE, stride,
                ctypes.c_void_p(offset),
            )
            offset += comps * 4

        glBindVertexArray(0)

    def draw(self) -> None:
        glBindVertexArray(self._vao)
        glDrawElements(GL_TRIANGLES, self._index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def dispose(self) -> None:
        glDeleteBuffers(1, [self._vbo])
        glDeleteBuffers(1, [self._ebo])
        glDeleteVertexArrays(1, [self._vao])
