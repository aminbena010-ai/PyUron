"""Renderer OpenGL 3.3 Core: estado global + dibujo con uniforms."""
from __future__ import annotations

from typing import Any

import numpy as np
from OpenGL.GL import (
    GL_BLEND, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, GL_DEPTH_TEST,
    GL_LEQUAL, GL_ONE_MINUS_SRC_ALPHA, GL_SRC_ALPHA, GL_VERSION,
    glBlendFunc, glClear, glClearColor, glDepthFunc, glDisable, glEnable,
    glGetString, glViewport,
)

from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader


class Renderer:
    def __init__(self, width: int, height: int, clear_color: tuple[float, ...]) -> None:
        self.clear_color = clear_color
        self.resize(width, height)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        raw = glGetString(GL_VERSION)
        if raw is None:
            raise RuntimeError(
                "Contexto OpenGL creado pero GL_VERSION no disponible. "
                "Comprueba que el driver soporta OpenGL 3.3 Core."
            )
        self.version = (
            raw.decode("utf-8", errors="replace")
            if isinstance(raw, (bytes, bytearray))
            else str(raw)
        )

    def resize(self, width: int, height: int) -> None:
        self.width = max(1, width)
        self.height = max(1, height)
        glViewport(0, 0, self.width, self.height)

    def begin_frame(self) -> None:
        glClearColor(*self.clear_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def draw(
        self,
        mesh: Mesh,
        shader: Shader,
        uniforms: dict[str, Any] | None = None,
    ) -> None:
        """Vincula shader → aplica uniforms → dibuja.

        Los uniforms se resuelven por tipo:
          - np.ndarray (4, 4)        → set_mat4
          - tuple (x, y, z)          → set_vec3
          - int / float              → set_float
        """
        shader.use()
        if uniforms:
            for name, value in uniforms.items():
                if isinstance(value, np.ndarray) and value.shape == (4, 4):
                    shader.set_mat4(name, value)
                elif isinstance(value, tuple) and len(value) == 3:
                    shader.set_vec3(name, *value)
                elif isinstance(value, (int, float)):
                    shader.set_float(name, float(value))
                else:
                    raise TypeError(
                        f"Uniform '{name}' con tipo no soportado: {type(value)}. "
                        f"Usa ndarray(4,4), tuple(3) o float."
                    )
        mesh.draw()

    def begin_2d_pass(self) -> None:
        """Desactiva depth test para dibujar sprites en orden de árbol."""
        glDisable(GL_DEPTH_TEST)

    def end_2d_pass(self) -> None:
        glEnable(GL_DEPTH_TEST)

    def end_frame(self) -> None:
        pass
