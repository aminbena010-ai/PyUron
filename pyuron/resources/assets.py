"""AssetManager: cachea y gestiona el ciclo de vida de shaders, texturas y mallas."""
from __future__ import annotations

from pathlib import Path

from pyuron.core.logger import Log
from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.resources.obj_loader import load_obj


class AssetManager:
    def __init__(self) -> None:
        self._shaders:  dict[tuple[str, str], Shader] = {}
        self._textures: dict[str, Texture2D]           = {}
        self._meshes:   dict[str, Mesh]                = {}

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

    # ── Liberación robusta ──────────────────────────────────────────
    def dispose_all(self) -> None:
        """Libera todos los recursos GPU sin detenerse si alguno falla."""
        for key, sh in list(self._shaders.items()):
            try:
                sh.dispose()
            except Exception as e:
                Log.warn(f"Error liberando shader {key}: {e}")
        self._shaders.clear()

        for key, tx in list(self._textures.items()):
            try:
                tx.dispose()
            except Exception as e:
                Log.warn(f"Error liberando textura {key}: {e}")
        self._textures.clear()

        for key, ms in list(self._meshes.items()):
            try:
                ms.dispose()
            except Exception as e:
                Log.warn(f"Error liberando malla {key}: {e}")
        self._meshes.clear()
