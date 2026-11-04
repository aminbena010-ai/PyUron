"""Cámara en primera persona: WASD + ratón capturado, yaw/pitch."""
from __future__ import annotations

import math

import numpy as np
import pygame

from pyuron.math import matrix
from pyuron.math.vector import Vector3
from pyuron.scene.node3d import Node3D


class FPSCameraNode(Node3D):
    def __init__(self, name: str = "FPSCamera") -> None:
        super().__init__(name)
        self.yaw = -90.0
        self.pitch = 0.0
        self.fov = 60.0
        self.near = 0.1
        self.far = 100.0
        self.move_speed = 3.0
        self.mouse_sensitivity = 0.12

        self._captured = False

    # ── Captura ratón ───────────────────────────────────────────────
    def capture_mouse(self) -> None:
        if not self._captured:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            pygame.mouse.get_rel()  # descartar el primer delta
            self._captured = True

    def release_mouse(self) -> None:
        if self._captured:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self._captured = False

    # ── Orientación ─────────────────────────────────────────────────
    def forward(self) -> Vector3:
        y = math.radians(self.yaw)
        p = math.radians(self.pitch)
        return Vector3(
            math.cos(p) * math.cos(y),
            math.sin(p),
            math.cos(p) * math.sin(y),
        )

    def right(self) -> Vector3:
        y = math.radians(self.yaw)
        return Vector3(-math.sin(y), 0.0, math.cos(y))

    # ── Actualización ───────────────────────────────────────────────
    def handle_input(self, dt: float) -> None:
        if not self._captured:
            return

        # Ratón
        dx, dy = pygame.mouse.get_rel()
        self.yaw   += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Teclado
        keys = pygame.key.get_pressed()
        speed = self.move_speed * dt
        if keys[pygame.K_LSHIFT]:
            speed *= 3.0

        fwd = self.forward()
        rgt = self.right()
        move = Vector3(0, 0, 0)
        if keys[pygame.K_w]: move = move + fwd
        if keys[pygame.K_s]: move = move - fwd
        if keys[pygame.K_d]: move = move + rgt
        if keys[pygame.K_a]: move = move - rgt
        if keys[pygame.K_SPACE] or keys[pygame.K_e]: move.y += 1.0
        if keys[pygame.K_LCTRL] or keys[pygame.K_q]: move.y -= 1.0

        if move.length() > 0:
            self.transform.position = self.transform.position + move * speed

    def view_projection(self, aspect: float) -> np.ndarray:
        proj = matrix.perspective(self.fov, aspect, self.near, self.far)
        p = self.world_position()
        f = self.forward()
        target = Vector3(p.x + f.x, p.y + f.y, p.z + f.z)
        view = matrix.look_at(
            (p.x, p.y, p.z),
            (target.x, target.y, target.z),
            (0.0, 1.0, 0.0),
        )
        return proj @ view

    def world_position(self) -> Vector3:
        pos = Vector3(0, 0, 0)
        node = self
        while node is not None:
            if isinstance(node, Node3D):
                pos = pos + node.transform.position
            node = node.parent
        return pos
