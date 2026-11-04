"""Mundo de física: integración + colisiones Box-Box, Sphere-Sphere, Sphere-Box."""
from __future__ import annotations

from pyuron.math.vector import Vector3
from pyuron.physics.shapes import SphereShape


class PhysicsWorld:
    def __init__(self, gravity: Vector3 | None = None, substeps: int = 2) -> None:
        self.gravity = gravity or Vector3(0.0, -9.8, 0.0)
        self.substeps = max(1, substeps)
        self.bodies: list = []
        self.slop = 1e-4  # tolerancia muy pequeña para no perder penetraciones

    def step(self, dt: float) -> None:
        if dt <= 0.0 or not self.bodies:
            return
        sub_dt = dt / self.substeps
        for _ in range(self.substeps):
            self._step_internal(sub_dt)

    def _step_internal(self, dt: float) -> None:
        for body in self.bodies:
            if body.is_static:
                continue
            if body.use_gravity:
                body.velocity = body.velocity + self.gravity * dt
            body.velocity = body.velocity * (body.linear_damping ** (dt * 60.0))
            if body.velocity.length() < 1e-4:  # solo drift numérico
                body.velocity = Vector3(0, 0, 0)
            body.transform.position = body.transform.position + body.velocity * dt

        for _ in range(3):
            for i in range(len(self.bodies)):
                for j in range(i + 1, len(self.bodies)):
                    self._dispatch(self.bodies[i], self.bodies[j])

    # ── Dispatch por tipo de forma ─────────────────────────────────
    def _dispatch(self, a, b) -> None:
        a_sph = isinstance(a.shape, SphereShape)
        b_sph = isinstance(b.shape, SphereShape)
        if a_sph and b_sph:
            self._resolve_sphere_sphere(a, b)
        elif a_sph and not b_sph:
            self._resolve_sphere_box(a, b)
        elif b_sph and not a_sph:
            self._resolve_sphere_box(b, a)
        else:
            self._resolve_box_box(a, b)

    # ── Box ↔ Box (eje de menor penetración) ─────────────────────
    def _resolve_box_box(self, a, b) -> None:
        aabb_a = a.get_aabb()
        aabb_b = b.get_aabb()
        ov = aabb_a.overlap(aabb_b)
        if ov is None:
            return
        if ov.x <= ov.y and ov.x <= ov.z:
            axis, depth = 0, ov.x
        elif ov.y <= ov.z:
            axis, depth = 1, ov.y
        else:
            axis, depth = 2, ov.z
        if depth < self.slop:
            return

        ca, cb = aabb_a.center(), aabb_b.center()
        if axis == 0:
            sign = 1.0 if cb.x >= ca.x else -1.0
        elif axis == 1:
            sign = 1.0 if cb.y >= ca.y else -1.0
        else:
            sign = 1.0 if cb.z >= ca.z else -1.0

        normal = Vector3(
            sign if axis == 0 else 0.0,
            sign if axis == 1 else 0.0,
            sign if axis == 2 else 0.0,
        )
        self._apply_push_and_bounce(a, b, normal, depth)

    # ── Sphere ↔ Sphere ──────────────────────────────────────────
    def _resolve_sphere_sphere(self, a, b) -> None:
        ca = a.world_position()
        cb = b.world_position()
        ra = a.shape.effective_radius(a.transform.scale)
        rb = b.shape.effective_radius(b.transform.scale)

        diff = cb - ca
        dist = diff.length()
        min_dist = ra + rb
        if dist >= min_dist:
            return
        if dist < 1e-8:
            diff = Vector3(1.0, 0.0, 0.0)
            dist = 1e-8
        normal = diff / dist
        self._apply_push_and_bounce(a, b, normal, min_dist - dist)

    # ── Sphere ↔ Box (punto más cercano de la caja al centro de la esfera) ──
    def _resolve_sphere_box(self, sphere, box) -> None:
        aabb = box.get_aabb()
        sc = sphere.world_position()
        sr = sphere.shape.effective_radius(sphere.transform.scale)

        # Punto más cercano de la caja al centro de la esfera
        closest = Vector3(
            max(aabb.min.x, min(sc.x, aabb.max.x)),
            max(aabb.min.y, min(sc.y, aabb.max.y)),
            max(aabb.min.z, min(sc.z, aabb.max.z)),
        )
        diff = sc - closest
        dist = diff.length()
        if dist >= sr:
            return

        if dist < 1e-8:
            # Centro dentro de la caja: empujar por el eje de menor penetración
            bc = aabb.center()
            ov = aabb.overlap(sphere.get_aabb())
            if ov is None:
                return
            if ov.x <= ov.y and ov.x <= ov.z:
                axis, depth = 0, ov.x + sr
            elif ov.y <= ov.z:
                axis, depth = 1, ov.y + sr
            else:
                axis, depth = 2, ov.z + sr
            sign = 1.0 if sc.x >= bc.x else -1.0 if axis == 0 else (
                1.0 if sc.y >= bc.y else -1.0 if axis == 1 else (
                    1.0 if sc.z >= bc.z else -1.0))
            normal = Vector3(
                sign if axis == 0 else 0.0,
                sign if axis == 1 else 0.0,
                sign if axis == 2 else 0.0,
            )
            self._apply_push_and_bounce(box, sphere, normal, depth)
            return

        normal = diff / dist
        self._apply_push_and_bounce(box, sphere, normal, sr - dist)

    # ── Empuje + rebote genérico (normal arbitraria) ──────────────
    def _apply_push_and_bounce(self, a, b, normal: Vector3, depth: float) -> None:
        """Normal apunta de a hacia b; separa los cuerpos `depth`."""
        if a.is_static and b.is_static:
            return
        if a.is_static:
            b.transform.position = b.transform.position + normal * depth
            self._reflect(b, normal)
        elif b.is_static:
            a.transform.position = a.transform.position + normal * -depth
            self._reflect(a, normal * -1.0)
        else:
            total_mass = a.mass + b.mass
            a_ratio = b.mass / total_mass
            b_ratio = a.mass / total_mass
            a.transform.position = a.transform.position + normal * (-depth * a_ratio)
            b.transform.position = b.transform.position + normal * (depth * b_ratio)
            self._reflect(a, normal * -1.0)
            self._reflect(b, normal)

    @staticmethod
    def _reflect(body, normal: Vector3) -> None:
        v = body.velocity
        vn = v.x * normal.x + v.y * normal.y + v.z * normal.z
        if vn >= 0:
            return
        scale = -(1.0 + body.restitution) * vn
        new_v = Vector3(
            v.x + scale * normal.x,
            v.y + scale * normal.y,
            v.z + scale * normal.z,
        )
        # Umbral de reposo
        if abs(new_v.x) < 0.1 and abs(new_v.z) < 0.1 and abs(new_v.y) < 0.1:
            body.velocity = Vector3(0, 0, 0)
        else:
            body.velocity = new_v
