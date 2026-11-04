"""PyUron public API."""

from pyuron.audio import AudioManager, make_tone
from pyuron.core.banner import show_banner
from pyuron.core.config import EngineConfig
from pyuron.core.engine import Engine
from pyuron.core.errors import install_exception_hook
from pyuron.core.logger import Log
from pyuron.core.timer import Cooldown, Stopwatch
from pyuron.core.timing import Timer, timed
from pyuron.graphics.camera import Camera2D, Camera3D
from pyuron.graphics.material import Material
from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader
from pyuron.graphics.sprite_quad import dispose_sprite_quad, get_sprite_quad
from pyuron.graphics.texture import Texture2D
from pyuron.input import InputManager
from pyuron.math import AABB, Transform, Vector2, Vector3
from pyuron.physics import (
    BoxShape, PhysicsWorld, RayHit, Shape, SphereShape, raycast,
)
from pyuron.resources.assets import AssetManager
from pyuron.scene import (
    Anchor,
    AnimatedSprite2D, Camera2DNode, Camera3DNode, FPSCameraNode,
    DirectionalLightNode, LabelNode, PointLightNode,
    MeshInstance2D, MeshInstance3D,
    Node, Node2D, Node3D, Scene, Sprite2D,
    PhysicsBody3D, SphereBody3D,
)
from pyuron.scene.label_node import render_text_surface, surface_to_array

from pyuron.core.version import __version__

__all__ = [
    "Engine", "EngineConfig", "Log", "Timer", "timed",
    "show_banner", "install_exception_hook",
    "InputManager", "AudioManager", "make_tone",
    "Cooldown", "Stopwatch",
    "Vector2", "Vector3", "Transform", "AABB",
    "Camera2D", "Camera3D",
    "Shader", "Mesh", "Material", "Texture2D", "AssetManager",
    "get_sprite_quad", "dispose_sprite_quad",
    "PhysicsWorld", "Shape", "BoxShape", "SphereShape", "RayHit", "raycast",
    "Node", "Node2D", "Node3D", "Scene",
    "PhysicsBody3D", "SphereBody3D",
    "MeshInstance2D", "MeshInstance3D",
    "Sprite2D", "AnimatedSprite2D", "LabelNode", "Anchor",
    "render_text_surface", "surface_to_array",
    "Camera2DNode", "Camera3DNode", "FPSCameraNode",
    "DirectionalLightNode", "PointLightNode",
    "__version__",
]
