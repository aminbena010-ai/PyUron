"""Escena: renderiza el árbol y avanza la física."""
from __future__ import annotations

from pyuron.physics.world import PhysicsWorld
from pyuron.scene.camera_node import _BaseCameraNode
from pyuron.scene.fps_camera import FPSCameraNode
from pyuron.scene.light_node import DirectionalLightNode, PointLightNode
from pyuron.scene.mesh_instance import _MeshInstanceBase
from pyuron.scene.node import Node
from pyuron.scene.physics_body import PhysicsBody3D
from pyuron.scene.sprite2d import Sprite2D


class Scene(Node):
    def __init__(self, name: str = "Scene") -> None:
        super().__init__(name)
        self.physics_world = PhysicsWorld()
        self.background_color: tuple[float, float, float, float] | None = None

    def _iter_tree(self):
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def _process(self, dt: float) -> None:
        # 1. Recolectar cuerpos y avanzar física
        self.physics_world.bodies = [
            n for n in self._iter_tree() if isinstance(n, PhysicsBody3D)
        ]
        self.physics_world.step(dt)

        # 2. Update de nodos (llama a Node.update)
        super()._process(dt)

    # ── Cámara y luces ──────────────────────────────────────────────
    def find_active_camera(self):
        for node in self._iter_tree():
            if isinstance(node, (_BaseCameraNode, FPSCameraNode)) and getattr(node, "active", True):
                return node
        return None

    def collect_lights(self):
        dir_lights: list[DirectionalLightNode] = []
        point_lights: list[PointLightNode] = []
        for node in self._iter_tree():
            if isinstance(node, DirectionalLightNode):
                dir_lights.append(node)
            elif isinstance(node, PointLightNode):
                point_lights.append(node)
        return dir_lights[:1], point_lights[:4]

    # ── Raycast ────────────────────────────────────────────────────
    def raycast(self, origin, direction, max_dist: float = 1000.0, ignore=None):
        """Devuelve el RayHit más cercano o None. Ver pyuron.physics.raycast."""
        from pyuron.physics.raycast import raycast
        bodies = [n for n in self._iter_tree() if isinstance(n, PhysicsBody3D)]
        return raycast(bodies, origin, direction, max_dist, ignore=ignore)

    # ── Serialización ──────────────────────────────────────────────
    def save_json(self, path) -> None:
        from pyuron.scene.serialization import save_scene
        save_scene(self, path)

    @staticmethod
    def load_json(path, sprite_shader=None, textures=None):
        from pyuron.scene.serialization import load_scene
        ctx = {"sprite_shader": sprite_shader, "textures": textures or {}}
        return load_scene(path, ctx)

    def render(self, renderer) -> None:
        camera = self.find_active_camera()
        if camera is None:
            return
        aspect = renderer.width / renderer.height
        vp = camera.view_projection(aspect)
        cam_pos = camera.world_position() if hasattr(camera, "world_position") else camera.transform.position

        dir_lights, point_lights = self.collect_lights()

        if dir_lights:
            dl = dir_lights[0]
            d = dl.direction()
            light_uniforms = {
                "u_dir_light_dir":       (d.x, d.y, d.z),
                "u_dir_light_color":     (dl.color.x, dl.color.y, dl.color.z),
                "u_dir_light_intensity": float(dl.intensity),
            }
        else:
            light_uniforms = {
                "u_dir_light_dir":       (0.0, 0.0, -1.0),
                "u_dir_light_color":     (0.0, 0.0, 0.0),
                "u_dir_light_intensity": 0.0,
            }

        light_uniforms["u_camera_pos"]   = (cam_pos.x, cam_pos.y, cam_pos.z)
        light_uniforms["u_point_count"]  = len(point_lights)

        if point_lights:
            positions, colors, intensities, attens = [], [], [], []
            for pl in point_lights:
                wp = pl.world_position()
                positions.append((wp.x, wp.y, wp.z))
                colors.append((pl.color.x, pl.color.y, pl.color.z))
                intensities.append(pl.intensity)
                attens.append(pl.attenuation)
            light_uniforms["u_point_pos"]       = positions
            light_uniforms["u_point_color"]     = colors
            light_uniforms["u_point_intensity"] = intensities
            light_uniforms["u_point_atten"]     = attens

        for node in self._iter_tree():
            if isinstance(node, _MeshInstanceBase):
                node.render(renderer, vp, light_uniforms)

        # Pass 2D: sprites ordenados por z_index, depth test desactivado
        sprites = [n for n in self._iter_tree() if isinstance(n, Sprite2D)]
        if sprites:
            sprites.sort(key=lambda s: (s.z_index, id(s)))
            renderer.begin_2d_pass()
            for sp in sprites:
                sp.render(renderer, vp)
            renderer.end_2d_pass()
