"""Material: shader + uniforms + texturas."""
from __future__ import annotations

from typing import Any

import numpy as np

from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D


class Material:
    def __init__(self, shader: Shader, uniforms: dict[str, Any] | None = None,
                 textures: dict[str, Texture2D] | None = None) -> None:
        self.shader = shader
        self.uniforms: dict[str, Any] = dict(uniforms or {})
        self.textures: dict[str, Texture2D] = dict(textures or {})

    def apply(self, extra_uniforms: dict[str, Any] | None = None) -> None:
        self.shader.use()

        for unit, (name, tex) in enumerate(self.textures.items()):
            tex.bind(unit)
            self.shader.set_int(name, unit)

        merged = {**self.uniforms, **(extra_uniforms or {})}
        for name, value in merged.items():
            if isinstance(value, np.ndarray) and value.shape == (4, 4):
                self.shader.set_mat4(name, value)
            elif isinstance(value, tuple) and len(value) == 3:
                self.shader.set_vec3(name, *value)
            elif isinstance(value, tuple) and len(value) == 4:
                self.shader.set_vec4(name, *value)
            elif isinstance(value, int):
                self.shader.set_int(name, value)
            elif isinstance(value, float):
                self.shader.set_float(name, value)
            elif isinstance(value, list) and value and isinstance(value[0], tuple):
                self.shader.set_vec3_array(name, value)
            elif isinstance(value, list) and value and isinstance(value[0], (int, float)):
                self.shader.set_float_array(name, value)
            else:
                raise TypeError(f"Uniform '{name}' tipo no soportado: {type(value)}")
