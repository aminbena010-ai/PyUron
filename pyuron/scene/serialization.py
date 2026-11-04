"""Serialización de escenas a JSON."""
from __future__ import annotations

import json
from pathlib import Path


# ── Registro de tipos de nodo ────────────────────────────────────
_REGISTRY: dict[str, type] = {}


def register_node_type(cls: type) -> type:
    """Registra una clase de nodo para que `from_dict` la encuentre."""
    _REGISTRY[cls.__name__] = cls
    return cls


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

    # Luces
    if isinstance(node, DirectionalLightNode):
        d["color"] = node.color.to_dict()
        d["intensity"] = node.intensity
    elif isinstance(node, PointLightNode):
        d["color"] = node.color.to_dict()
        d["intensity"] = node.intensity
        d["attenuation"] = list(node.attenuation)

    # Física
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

    # Sprites
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
    """Crea el nodo correspondiente. Requiere que el tipo esté registrado."""
    from pyuron.math import Vector3
    from pyuron.scene.physics_body import PhysicsBody3D
    from pyuron.physics.shapes import BoxShape, SphereShape
    from pyuron.scene.light_node import DirectionalLightNode, PointLightNode
    from pyuron.scene.sprite2d import Sprite2D
    from pyuron.scene.animated_sprite2d import AnimatedSprite2D
    from pyuron.scene.label_node import LabelNode

    type_name = d["type"]
    cls = _REGISTRY.get(type_name)
    if cls is None:
        raise ValueError(
            f"Tipo de nodo no registrado: '{type_name}'. "
            f"Registrados: {sorted(_REGISTRY.keys())}"
        )

    # Nodos que requieren argumentos especiales
    if type_name == "Sprite2D" or type_name == "AnimatedSprite2D" or type_name == "LabelNode":
        # Usan un shader/textura compartida del contexto
        shader = scene_context.get("sprite_shader")
        if shader is None:
            raise ValueError(f"{type_name} requiere 'sprite_shader' en el contexto.")

        if type_name == "AnimatedSprite2D":
            tex_key = f"tex_{d['name']}"
            tex = scene_context.get("textures", {}).get(tex_key)
            if tex is None:
                raise ValueError(f"Textura '{tex_key}' no encontrada en contexto.")
            node = AnimatedSprite2D(tex, shader,
                                    frame_w=d["frame_w"], frame_h=d["frame_h"],
                                    name=d["name"])
            node.fps = d.get("fps", 10.0)
            node.loop_mode = d.get("loop_mode", "loop")
            node.current_frame = d.get("current_frame", 0)
        elif type_name == "LabelNode":
            node = LabelNode(
                text=d.get("text", ""),
                font_size=d.get("font_size", 24),
                shader=shader,
                color=tuple(d.get("color", (255, 255, 255, 255))),
                name=d["name"],
            )
        else:  # Sprite2D
            tex_key = f"tex_{d['name']}"
            tex = scene_context.get("textures", {}).get(tex_key)
            if tex is None:
                raise ValueError(f"Textura '{tex_key}' no encontrada en contexto.")
            node = Sprite2D(tex, shader, name=d["name"])

        # Sprite props
        if d.get("size") is not None:
            node.size = tuple(d["size"])
        node.ppu = d.get("ppu", 64.0)
        node.tint = tuple(d.get("tint", (1.0, 1.0, 1.0, 1.0)))
        node.flip_x = d.get("flip_x", False)
        node.flip_y = d.get("flip_y", False)
        node.z_index = d.get("z_index", 0)
    elif type_name == "SphereBody3D":
        node = cls(d["name"], radius=d.get("shape", {}).get("radius", 0.5))
    elif type_name == "PhysicsBody3D":
        node = PhysicsBody3D(d["name"])
    elif type_name == "DirectionalLightNode":
        node = DirectionalLightNode(d["name"])
    elif type_name == "PointLightNode":
        node = PointLightNode(d["name"])
    else:
        node = cls(d.get("name", type_name))

    # Comunes
    node.name = d.get("name", node.name)
    node.visible = d.get("visible", True)

    if "transform" in d and hasattr(node, "transform"):
        node.transform.load_dict(d["transform"])

    # Luces
    if isinstance(node, (DirectionalLightNode, PointLightNode)):
        if "color" in d:
            node.color = Vector3.from_dict(d["color"])
        node.intensity = d.get("intensity", node.intensity)
        if isinstance(node, PointLightNode) and "attenuation" in d:
            node.attenuation = tuple(d["attenuation"])

    # Física
    if isinstance(node, PhysicsBody3D):
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

    # Hijos (recursivo)
    for child_dict in d.get("children", []):
        child = _dict_to_node(child_dict, scene_context)
        node.add_child(child)

    return node


# ── API pública ─────────────────────────────────────────────────
def scene_to_dict(scene) -> dict:
    return {
        "version": "1.0.0",
        "scene": _node_to_dict(scene),
    }


def save_scene(scene, path: str | Path) -> None:
    data = scene_to_dict(scene)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_scene(path: str | Path, scene_context: dict):
    """Carga una escena. `scene_context` debe tener:
       - "sprite_shader": Shader
       - "textures": dict[str, Texture2D] con claves f"tex_{node_name}"
    """
    from pyuron.scene.scene import Scene

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    scene_dict = data["scene"]
    root = _dict_to_node(scene_dict, scene_context)

    # Forzar que el root sea Scene
    if not isinstance(root, Scene):
        scene = Scene(scene_dict.get("name", "Scene"))
        for child in root.children[:]:
            scene.add_child(child)
        return scene
    return root
