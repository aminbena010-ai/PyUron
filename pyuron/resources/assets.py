"""AssetManager: cachea shaders, texturas y mallas por ruta."""
from __future__ import annotations

from pathlib import Path

from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.resources.obj_loader import load_obj


class AssetManager:
    def __init__(self) -> None:
        self._shaders:  dict[tuple[str, str], Shader]    = {}
        self._textures: dict[str, Texture2D]             = {}
        self._meshes:   dict[str, Mesh]                  = {}

    # ── Shaders ─────────────────────────────────────────────────────
    def get_shader(self, vert: str | Path, frag: str | Path) -> Shader:
        key = (str(vert), str(frag))
        if key not in self._shaders:
            self._shaders[key] = Shader.from_files(vert, frag)
        return self._shaders[key]

    # ── Texturas ────────────────────────────────────────────────────
    def get_texture(self, path: str | Path) -> Texture2D:
        key = str(path)
        if key not in self._textures:
            self._textures[key] = Texture2D.from_file(path)
        return self._textures[key]

    # ── Mallas ──────────────────────────────────────────────────────
    def get_mesh(self, path: str | Path) -> Mesh:
        key = str(path)
        if key not in self._meshes:
            vertices, indices = load_obj(path)
            mesh = Mesh(
                vertices,
                indices,
                layout=[(0, 3), (1, 3), (2, 2)],  # pos, normal, uv
            )
            self._meshes[key] = mesh
        return self._meshes[key]

    def dispose_all(self) -> None:
        for sh in self._shaders.values():  sh.dispose()
        for tx in self._textures.values(): tx.dispose()
        for ms in self._meshes.values():   ms.dispose()
        self._shaders.clear()
        self._textures.clear()
        self._meshes.clear()
