"""PyUron 0.3 — Demo: escena con cámara, textura procedural y cuadrado girando."""
from __future__ import annotations

from pyuron import (
    Engine, EngineConfig, Log, __version__,
    install_exception_hook, show_banner,
)
from pyuron.graphics.material import Material
from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.math import Vector3
from pyuron.scene import Camera3DNode, MeshInstance3D, Node3D, Scene


SHADER_DIR = "assets/shaders"


def make_quad_mesh() -> Mesh:
    vertices = [
        (-0.5, -0.5, 0.0,   0.0, 0.0),
        ( 0.5, -0.5, 0.0,   1.0, 0.0),
        ( 0.5,  0.5, 0.0,   1.0, 1.0),
        (-0.5,  0.5, 0.0,   0.0, 1.0),
    ]
    indices = [0, 1, 2, 0, 2, 3]
    return Mesh(vertices, indices, layout=[(0, 3), (1, 2)])


def main() -> None:
    install_exception_hook()
    show_banner(__version__)

    config = EngineConfig(
        title=f"PyUron {__version__} — Escena",
        width=1280, height=720,
        resizable=True, vsync=True,
        clear_color=(0.045, 0.055, 0.075, 1.0),
    )

    engine = Engine(config)
    engine.initialize()

    # ── Recursos ──────────────────────────────────────────────────
    shader = Shader.from_files(f"{SHADER_DIR}/basic.vert",
                               f"{SHADER_DIR}/basic.frag")
    Log.ok("Shader cargado desde assets/shaders/")

    texture = Texture2D.checker(width=512, height=512, cell=64)
    Log.ok(f"Textura procedural: {texture.width}×{texture.height}")

    material = Material(
        shader=shader,
        uniforms={"u_tint": (1.0, 0.85, 0.45)},
        textures={"u_texture": texture},
    )
    mesh = make_quad_mesh()

    # ── Escena ────────────────────────────────────────────────────
    scene = Scene("MainScene")

    camera = Camera3DNode("Camera")
    camera.transform.position = Vector3(0.0, 0.0, 2.5)   # API unificada
    camera.target = Vector3(0.0, 0.0, 0.0)
    scene.add_child(camera)

    root = Node3D("Root")
    scene.add_child(root)

    quad = MeshInstance3D(mesh, material, "Quad")
    quad.transform.scale = Vector3(1.5, 1.5, 1.0)
    root.add_child(quad)

    engine.set_scene(scene)
    Log.ok("Escena lista — cierra la ventana para salir")

    state = {"angle": 0.0}

    def update(dt: float) -> None:
        state["angle"] += dt * 45.0
        quad.transform.rotation = Vector3(0.0, state["angle"] * 0.6, state["angle"])

    engine.on_update(update)
    engine.run()

    shader.dispose()
    texture.dispose()
    mesh.dispose()


if __name__ == "__main__":
    main()
