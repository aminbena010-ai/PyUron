"""Material: shader + uniforms + texturas, todo lo que necesita un draw."""
from __future__ import annotations

from typing import Any

import numpy as np

from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D


class Material:
    def __init__(
        self,
        shader: Shader,
        uniforms: dict[str, Any] | None = None,
        textures: dict[str, Texture2D] | None = None,
    ) -> None:
        self.shader = shader
        self.uniforms: dict[str, Any] = dict(uniforms or {})
        self.textures: dict[str, Texture2D] = dict(textures or {})

    def apply(self, extra_uniforms: dict[str, Any] | None = None) -> None:
        """Vincula shader, sube uniforms y bindea texturas."""
        self.shader.use()

        # Texturas: asignamos unidad 0, 1, 2, ... por orden de dict.
        for unit, (name, tex) in enumerate(self.textures.items()):
            tex.bind(unit)
            self.shader.set_int(name, unit)

        # Uniforms de usuario + extras (por ejemplo u_mvp).
        all_uniforms: dict[str, Any] = {**self.uniforms, **(extra_uniforms or {})}
        for name, value in all_uniforms.items():
            if isinstance(value, np.ndarray) and value.shape == (4, 4):
                self.shader.set_mat4(name, value)
            elif isinstance(value, tuple) and len(value) == 3:
                self.shader.set_vec3(name, *value)
            elif isinstance(value, (int, float)):
                self.shader.set_float(name, float(value))
            else:
                raise TypeError(
                    f"Uniform '{name}' con tipo no soportado: {type(value)}"
                )
