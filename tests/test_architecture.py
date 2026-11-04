"""Comprobaciones arquitectónicas: límites de import y API pública."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pyuron

ROOT = Path(__file__).resolve().parent.parent


def _run(code: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    for line in result.stdout.splitlines():
        if line.startswith("RESULT"):
            return line[len("RESULT"):].strip()
    raise AssertionError(f"Sin salida RESULT: {result.stdout!r}")


def test_import_does_not_initialize_display_or_optional_editor():
    out = _run(
        "import pyuron, pygame, sys;"
        "print('RESULT', pygame.display.get_init(),"
        " pygame.font.get_init(), pygame.mixer.get_init() is None,"
        " 'PySide6' in sys.modules)"
    )
    assert out == "False False True False"


def test_node_types_are_not_registered_at_import():
    out = _run(
        "import pyuron.scene.serialization as s; import pyuron.scene;"
        "print('RESULT', s._defaults_registered, 'Scene' in s._REGISTRY)"
    )
    assert out == "False False"


def test_default_node_types_registration_is_idempotent():
    out = _run(
        "import pyuron.scene.serialization as s;"
        "s.ensure_default_node_types(); s.ensure_default_node_types();"
        "print('RESULT', len(s._REGISTRY), 'Scene' in s._REGISTRY)"
    )
    count, has_scene = out.split()
    assert int(count) >= 16
    assert has_scene == "True"


def _module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _module_level_imports(tree: ast.Module) -> set[str]:
    targets: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("pyuron"):
                targets.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("pyuron"):
                    targets.add(alias.name)
    return targets


def test_no_module_level_import_cycles():
    graph: dict[str, set[str]] = {}
    for path in (ROOT / "pyuron").rglob("*.py"):
        name = _module_name(path)
        graph[name] = _module_level_imports(ast.parse(path.read_text(encoding="utf-8")))

    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[list[str]] = []

    def visit(node: str, path: list[str]) -> None:
        if node in visited:
            return
        if node in visiting:
            start = path.index(node)
            cycles.append(path[start:] + [node])
            return
        visiting.add(node)
        for dep in graph.get(node, ()):
            if dep in graph:
                visit(dep, path + [dep])
        visiting.discard(node)
        visited.add(node)

    for module in graph:
        visit(module, [module])

    assert cycles == []


def test_public_api_is_stable():
    expected = {
        "Engine", "EngineConfig", "Log", "Timer", "timed",
        "InputManager", "AudioManager", "make_tone",
        "Vector2", "Vector3", "Transform", "AABB",
        "Camera2D", "Camera3D", "Shader", "Mesh", "Material",
        "Texture2D", "AssetManager",
        "PhysicsWorld", "Shape", "BoxShape", "SphereShape", "RayHit", "raycast",
        "Node", "Node2D", "Node3D", "Scene",
        "PhysicsBody3D", "SphereBody3D",
        "MeshInstance2D", "MeshInstance3D",
        "Sprite2D", "AnimatedSprite2D", "LabelNode", "Anchor",
        "Camera2DNode", "Camera3DNode", "FPSCameraNode",
        "DirectionalLightNode", "PointLightNode", "__version__",
    }
    assert expected.issubset(set(pyuron.__all__))
    for name in pyuron.__all__:
        assert hasattr(pyuron, name), name
    assert len(pyuron.__all__) == len(set(pyuron.__all__))
