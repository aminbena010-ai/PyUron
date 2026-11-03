"""Shader GLSL 330 con compilación, link, caché de uniforms y validación."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from OpenGL.GL import (
    GL_COMPILE_STATUS, GL_CURRENT_PROGRAM, GL_FRAGMENT_SHADER,
    GL_LINK_STATUS, GL_TRUE, GL_VERTEX_SHADER,
    glAttachShader, glCompileShader, glCreateProgram, glCreateShader,
    glDeleteProgram, glDeleteShader, glGetIntegerv, glGetProgramInfoLog,
    glGetProgramiv, glGetShaderInfoLog, glGetShaderiv, glGetUniformLocation,
    glLinkProgram, glShaderSource, glUniform1f, glUniform1i, glUniform3f,
    glUniformMatrix4fv, glUseProgram,
)


class Shader:
    def __init__(self, vertex_src: str, fragment_src: str) -> None:
        self._uniforms: dict[str, int] = {}
        self.program = self._build(vertex_src, fragment_src)

    # ── Carga desde archivos ────────────────────────────────────────
    @classmethod
    def from_files(cls, vert: str | Path, frag: str | Path) -> "Shader":
        v = Path(vert).read_text(encoding="utf-8")
        f = Path(frag).read_text(encoding="utf-8")
        return cls(v, f)

    # ── Compilación / link ──────────────────────────────────────────
    def _compile(self, src: str, kind: int) -> int:
        sh = glCreateShader(kind)
        glShaderSource(sh, src)
        glCompileShader(sh)
        if not glGetShaderiv(sh, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(sh)
            glDeleteShader(sh)
            kind_name = "vertex" if kind == GL_VERTEX_SHADER else "fragment"
            raise RuntimeError(f"Fallo al compilar shader {kind_name}:\n{log}")
        return sh

    def _build(self, vertex_src: str, fragment_src: str) -> int:
        vs = self._compile(vertex_src, GL_VERTEX_SHADER)
        fs = self._compile(fragment_src, GL_FRAGMENT_SHADER)
        prog = glCreateProgram()
        glAttachShader(prog, vs); glAttachShader(prog, fs)
        glLinkProgram(prog)
        if not glGetProgramiv(prog, GL_LINK_STATUS):
            log = glGetProgramInfoLog(prog)
            glDeleteProgram(prog)
            raise RuntimeError(f"Fallo al linquear programa:\n{log}")
        glDeleteShader(vs); glDeleteShader(fs)
        return prog

    # ── Vinculación ─────────────────────────────────────────────────
    def use(self) -> None:
        glUseProgram(self.program)

    def _ensure_bound(self, method_name: str) -> None:
        if int(glGetIntegerv(GL_CURRENT_PROGRAM)) != self.program:
            raise RuntimeError(
                f"{method_name}() llamado sin shader.use() previo. "
                f"Patrón: shader.use() → shader.set_*() → mesh.draw()"
            )

    def _loc(self, name: str) -> int:
        if name not in self._uniforms:
            self._uniforms[name] = glGetUniformLocation(self.program, name)
        return self._uniforms[name]

    # ── Uniforms ────────────────────────────────────────────────────
    def set_mat4(self, name: str, mat: np.ndarray) -> None:
        loc = self._loc(name)
        if loc < 0: return
        self._ensure_bound("set_mat4")
        glUniformMatrix4fv(loc, 1, GL_TRUE,
                           np.ascontiguousarray(mat, dtype=np.float32).flatten())

    def set_vec3(self, name: str, x: float, y: float, z: float) -> None:
        loc = self._loc(name)
        if loc < 0: return
        self._ensure_bound("set_vec3")
        glUniform3f(loc, float(x), float(y), float(z))

    def set_float(self, name: str, value: float) -> None:
        loc = self._loc(name)
        if loc < 0: return
        self._ensure_bound("set_float")
        glUniform1f(loc, float(value))

    def set_int(self, name: str, value: int) -> None:
        loc = self._loc(name)
        if loc < 0: return
        self._ensure_bound("set_int")
        glUniform1i(loc, int(value))

    def dispose(self) -> None:
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0
