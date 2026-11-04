"""Raycast contra cuerpos de física (AABB y esferas)."""
from __future__ import annotations

from dataclasses import dataclass

from pyuron.math.aabb import AABB
from pyuron.math.vector import Vector3
from pyuron.physics.shapes import SphereShape


@dataclass
class RayHit:
    body: object
    point: Vector3
    normal: Vector3
    distance: float


def _ray_vs_aabb(origin: Vector3, dir: Vector3, aabb: AABB):
    tmin, tmax = -1e30, 1e30
    for o, d, mn, mx in (
        (origin.x, dir.x, aabb.min.x, aabb.max.x),
        (origin.y, dir.y, aabb.min.y, aabb.max.y),
        (origin.z, dir.z, aabb.min.z, aabb.max.z),
    ):
        if abs(d) < 1e-9:
            if o < mn or o > mx:
                return None
        else:
            t1 = (mn - o) / d
            t2 = (mx - o) / d
            if t1 > t2:
                t1, t2 = t2, t1
            if t1 > tmin:
                tmin = t1
            if t2 < tmax:
                tmax = t2
            if tmin > tmax:
                return None
    return (tmin, tmax)


def _ray_vs_sphere(origin: Vector3, dir: Vector3, center: Vector3, radius: float):
    oc = origin - center
    a = dir.x * dir.x + dir.y * dir.y + dir.z * dir.z
    b = 2.0 * (oc.x * dir.x + oc.y * dir.y + oc.z * dir.z)
    c = oc.x * oc.x + oc.y * oc.y + oc.z * oc.z - radius * radius
    disc = b * b - 4.0 * a * c
    if disc < 0:
        return None
    sd = disc ** 0.5
    return ((-b - sd) / (2.0 * a), (-b + sd) / (2.0 * a))


def raycast(
    bodies: list,
    origin: Vector3,
    direction: Vector3,
    max_dist: float = 1000.0,
    ignore=None,
) -> RayHit | None:
    d = direction.normalized()
    best: RayHit | None = None
    best_t = max_dist

    for body in bodies:
        if body is ignore:
            continue
        if isinstance(body.shape, SphereShape):
            c = body.world_position()
            r = body.shape.effective_radius(body.transform.scale)
            hit = _ray_vs_sphere(origin, d, c, r)
        else:
            hit = _ray_vs_aabb(origin, d, body.get_aabb())
        if hit is None:
            continue
        t_near, t_far = hit
        t = t_near if t_near >= 0 else t_far
        if t < 0 or t > best_t:
            continue

        point = origin + d * t

        if isinstance(body.shape, SphereShape):
            c = body.world_position()
            normal = (point - c).normalized()
        else:
            aabb = body.get_aabb()
            c = aabb.center()
            diff = point - c
            sx = max(aabb.size().x * 0.5, 1e-8)
            sy = max(aabb.size().y * 0.5, 1e-8)
            sz = max(aabb.size().z * 0.5, 1e-8)
            ax = abs(diff.x) / sx
            ay = abs(diff.y) / sy
            az = abs(diff.z) / sz
            if ax >= ay and ax >= az:
                normal = Vector3(1.0 if diff.x > 0 else -1.0, 0, 0)
            elif ay >= az:
                normal = Vector3(0, 1.0 if diff.y > 0 else -1.0, 0)
            else:
                normal = Vector3(0, 0, 1.0 if diff.z > 0 else -1.0)

        best_t = t
        best = RayHit(body=body, point=point, normal=normal, distance=t)

    return best
