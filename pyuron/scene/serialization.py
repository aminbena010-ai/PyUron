"""Serialización de escenas a JSON con validación y manejo robusto de errores."""
from __future__ import annotations

import json
from pathlib import Path

from pyuron.core.logger import Log
from pyuron.core.version import __version__


# ── Registro de tipos de nodo ────────────────────────────────────
_REGISTRY: dict[str, type] = {}
_defaults_registered: bool = False


def register_node_type(cls: type, force: bool = False) -> type:
    """Registra una clase de nodo. Lanza error si ya existe (a menos que force=True)."""
    name = cls.__name__
    if name in _REGISTRY and not force and _REGISTRY[name] is not cls:
        raise ValueError(
            f"El tipo '{name}' ya está registrado por otra clase. Usa force=True para sobrescribir."
        )
    _REGISTRY[name] = cls
    return cls


def ensure_default_node_types() -> None:
    """Registra los tipos del motor. Idempotente."""
    global _defaults_registered
    if _defaults_registered:
        return

    from pyuron.scene.node import Node
    from pyuron.scene.node2d import Node2D
    from pyuron.scene.node3d import Node3D
    from pyuron.scene.scene import Scene
    from pyuron.scene.mesh_instance import MeshInstance2D, MeshInstance3D
    from pyuron.scene.camera_node import Camera2DNode, Camera3DNode
    from pyuron.scene.fps_camera import FPSCameraNode
    from pyuron.scene.light_node import DirectionalLightNode, PointLightNode
    from pyuron.scene.physics_body import PhysicsBody3D, SphereBody3D
    from pyuron.scene.sprite2d import Sprite2D
    from pyuron.scene.animated_sprite2d import AnimatedSprite2D
    from pyuron.scene.label_node import LabelNode

    for cls in (
        Node, Node2D, Node3D, Scene,
        MeshInstance2D, MeshInstance3D,
        Camera2DNode, Camera3DNode, FPSCameraNode,
        DirectionalLightNode, PointLightNode,
        PhysicsBody3D, SphereBody3D,
        Sprite2D, AnimatedSprite2D, LabelNode,
    ):
        if _REGISTRY.get(cls.__name__) is not cls:
            register_node_type(cls)

    _defaults_registered = True


# ── Serialización por tipo ───────────────────────────────────────
def _node_to_dict(node) -> dict:
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.scene.sprite2d import Sprite2D
    from pyuron.scene.animated_sprite2d import AnimatedSprite2D
    from pyuron.scene.label_node import LabelNode
    from pyuron.scene.light_node import DirectionalLightNode, PointLightNode
    from pyuron.physics.shapes import SphereShape

    d: dict = {
        "type": node.__class__.__name__,
        "name": node.name,
        "visible": node.visible,
        "children": [_node_to_dict(c) for c in node.children],
    }

    if hasattr(node, "transform"):
        d["transform"] = node.transform.to_dict()

    if isinstance(node, DirectionalLightNode):
        d["color"] = node.color.to_dict()
        d["intensity"] = node.intensity
    elif isinstance(node, PointLightNode):
        d["color"] = node.color.to_dict()
        d["intensity"] = node.intensity
        d["attenuation"] = list(node.attenuation)

    if isinstance(node, PhysicsBody3D):
        if isinstance(node.shape, SphereShape):
            d["shape"] = {"type": "sphere", "radius": node.shape.radius}
        else:
            d["shape"] = {"type": "box", "size": node.shape.size.to_dict()}
        d["velocity"] = node.velocity.to_dict()
        d["is_static"] = node.is_static
        d["use_gravity"] = node.use_gravity
        d["mass"] = node.mass
        d["restitution"] = node.restitution
        d["linear_damping"] = node.linear_damping

    if isinstance(node, Sprite2D):
        d["size"] = list(node.size) if node.size else None
        d["ppu"] = node.ppu
        d["tint"] = list(node.tint)
        d["flip_x"] = node.flip_x
        d["flip_y"] = node.flip_y
        d["z_index"] = node.z_index
        if isinstance(node, AnimatedSprite2D):
            d["frame_w"] = node.frame_w
            d["frame_h"] = node.frame_h
            d["fps"] = node.fps
            d["loop_mode"] = node.loop_mode
            d["current_frame"] = node.current_frame
        if isinstance(node, LabelNode):
            d["text"] = node.text
            d["font_size"] = node.font_size
            d["color"] = list(node.color)

    return d


def _dict_to_node(d: dict, scene_context: dict):
    """Crea el nodo correspondiente con errores descriptivos si algo falla."""
    from pyuron.math import Vector3
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.physics.shapes import BoxShape, SphereShape
    from pyuron.scene.light_node import DirectionalLightNode, PointLightNode

    if not isinstance(d, dict):
        raise ValueError(f"Se esperaba un diccionario de nodo, se recibió {type(d).__name__}.")
    if "type" not in d:
        raise ValueError(f"Nodo sin clave 'type': {d.get('name', '?')}")
    type_name = d["type"]
    if type_name not in _REGISTRY:
        raise ValueError(
            f"Tipo de nodo no registrado: '{type_name}'. "
            f"Registrados: {sorted(_REGISTRY.keys())}"
        )
    if "name" not in d:
        raise ValueError(f"Nodo sin clave 'name' (tipo {type_name})")

    try:
        node = _instantiate_node(d, type_name, scene_context)
        _apply_common_properties(node, d, type_name, Vector3)
        _apply_specific_properties(node, d, type_name, Vector3, DirectionalLightNode, PointLightNode, PhysicsBody3D, BoxShape, SphereShape)

        # Hijos
        for child_dict in d.get("children", []):
            child = _dict_to_node(child_dict, scene_context)
            node.add_child(child)

        return node
    except Exception as e:
        raise ValueError(
            f"Error cargando nodo '{d.get('name')}' de tipo '{type_name}': {e}"
        ) from e


def _instantiate_node(d, type_name, scene_context):
    """Crea la instancia del nodo según su tipo."""
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.scene.light_node import DirectionalLightNode, PointLightNode
    from pyuron.scene.sprite2d import Sprite2D
    from pyuron.scene.animated_sprite2d import AnimatedSprite2D
    from pyuron.scene.label_node import LabelNode

    if type_name in ("Sprite2D", "AnimatedSprite2D", "LabelNode"):
        shader = scene_context.get("sprite_shader")
        if shader is None:
            raise ValueError(f"{type_name} requiere 'sprite_shader' en el contexto.")
        tex_key = f"tex_{d['name']}"
        tex = scene_context.get("textures", {}).get(tex_key)
        if tex is None:
            raise ValueError(f"Textura '{tex_key}' no encontrada en el contexto.")

        if type_name == "AnimatedSprite2D":
            return AnimatedSprite2D(tex, shader,
                                    frame_w=d["frame_w"], frame_h=d["frame_h"],
                                    name=d["name"])
        if type_name == "LabelNode":
            return LabelNode(text=d.get("text", ""),
                             font_size=d.get("font_size", 24),
                             shader=shader,
                             color=tuple(d.get("color", (255, 255, 255, 255))),
                             name=d["name"])
        return Sprite2D(tex, shader, name=d["name"])

    if type_name == "SphereBody3D":
        return cls_lookup(type_name)(d["name"], radius=d.get("shape", {}).get("radius", 0.5))
    if type_name == "PhysicsBody3D":
        return PhysicsBody3D(d["name"])
    if type_name == "DirectionalLightNode":
        return DirectionalLightNode(d["name"])
    if type_name == "PointLightNode":
        return PointLightNode(d["name"])
    return cls_lookup(type_name)(d["name"])


def _apply_common_properties(node, d, type_name, Vector3):
    node.name = d["name"]
    node.visible = d.get("visible", True)
    if "transform" in d and hasattr(node, "transform"):
        node.transform.load_dict(d["transform"])


def _apply_specific_properties(node, d, type_name, Vector3, DirLight, PointLight, PhysBody, BoxShape, SphereShape):
    from pyuron.scene.sprite2d import Sprite2D
    from pyuron.scene.animated_sprite2d import AnimatedSprite2D

    # Luces
    if isinstance(node, (DirLight, PointLight)):
        if "color" in d:
            node.color = Vector3.from_dict(d["color"])
        node.intensity = d.get("intensity", node.intensity)
        if isinstance(node, PointLight) and "attenuation" in d:
            node.attenuation = tuple(d["attenuation"])

    # Física
    if isinstance(node, PhysBody):
        if "shape" in d:
            sh = d["shape"]
            if sh.get("type") == "sphere":
                node.shape = SphereShape(sh.get("radius", 0.5))
            else:
                node.shape = BoxShape(Vector3.from_dict(sh.get("size", {})))
        if "velocity" in d:
            node.velocity = Vector3.from_dict(d["velocity"])
        node.is_static = d.get("is_static", False)
        node.use_gravity = d.get("use_gravity", True)
        node.mass = d.get("mass", 1.0)
        node.restitution = d.get("restitution", 0.05)
        node.linear_damping = d.get("linear_damping", 0.85)

    # Sprites
    if isinstance(node, Sprite2D):
        if d.get("size") is not None:
            node.size = tuple(d["size"])
        node.ppu = d.get("ppu", 64.0)
        node.tint = tuple(d.get("tint", (1.0, 1.0, 1.0, 1.0)))
        node.flip_x = d.get("flip_x", False)
        node.flip_y = d.get("flip_y", False)
        node.z_index = d.get("z_index", 0)
        if isinstance(node, AnimatedSprite2D):
            node.fps = d.get("fps", 10.0)
            node.loop_mode = d.get("loop_mode", "loop")
            node.current_frame = d.get("current_frame", 0)


def cls_lookup(name):
    """Obtiene la clase registrada por nombre (o lanza ValueError)."""
    if name not in _REGISTRY:
        raise ValueError(f"Tipo no registrado: '{name}'")
    return _REGISTRY[name]


# ── API pública ─────────────────────────────────────────────────
def scene_to_dict(scene) -> dict:
    return {"version": __version__, "scene": _node_to_dict(scene)}


def save_scene(scene, path: str | Path) -> None:
    data = scene_to_dict(scene)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_scene(path: str | Path, scene_context: dict):
    """Carga una escena con validación estricta de estructura."""
    from pyuron.scene.scene import Scene
    ensure_default_node_types()

    try:
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON inválido en {path}: {e}") from e

    if not isinstance(data, dict) or "scene" not in data:
        raise ValueError(f"Archivo de escena inválido: falta la clave raíz 'scene' en {path}")

    file_version = data.get("version", "unknown")
    if file_version != __version__:
        Log.warn(f"Cargando escena versión {file_version} (motor actual: {__version__}).")

    scene_dict = data["scene"]
    root = _dict_to_node(scene_dict, scene_context)

    if not isinstance(root, Scene):
        scene = Scene(scene_dict.get("name", "Scene"))
        for child in root.children[:]:
            scene.add_child(child)
        return scene
    return root
