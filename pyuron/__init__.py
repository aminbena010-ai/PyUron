"""PyUron public API."""

from pyuron.core.banner import show_banner
from pyuron.core.config import EngineConfig
from pyuron.core.engine import Engine
from pyuron.core.errors import install_exception_hook
from pyuron.core.logger import Log
from pyuron.core.timing import Timer, timed
from pyuron.graphics.camera import Camera2D, Camera3D
from pyuron.graphics.material import Material
from pyuron.graphics.mesh import Mesh
from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.math import Transform, Vector2, Vector3
from pyuron.scene import (
    Camera2DNode, Camera3DNode,
    MeshInstance2D, MeshInstance3D,
    Node, Node2D, Node3D, Scene,
)

__version__ = "0.3.0"

__all__ = [
    "Engine", "EngineConfig",
    "Log", "Timer", "timed",
    "show_banner", "install_exception_hook",
    "Vector2", "Vector3", "Transform",
    "Camera2D", "Camera3D",
    "Shader", "Mesh", "Material", "Texture2D",
    "Node", "Node2D", "Node3D", "Scene",
    "MeshInstance2D", "MeshInstance3D",
    "Camera2DNode", "Camera3DNode",
    "__version__",
]
