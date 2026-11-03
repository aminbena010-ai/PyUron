"""Matrices 4x4 en convención fila-mayor (row-major numpy).

Se pasan a OpenGL con transpose=GL_TRUE (ver Shader.set_mat4).
"""
from __future__ import annotations

import numpy as np


def identity() -> np.ndarray:
    return np.eye(4, dtype=np.float32)


def translate(x: float, y: float, z: float) -> np.ndarray:
    m = np.eye(4, dtype=np.float32)
    m[0, 3] = x; m[1, 3] = y; m[2, 3] = z
    return m


def scale(x: float, y: float, z: float) -> np.ndarray:
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = x; m[1, 1] = y; m[2, 2] = z
    return m


def rotate_x(deg: float) -> np.ndarray:
    a = np.radians(deg); c = np.cos(a); s = np.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[1, 1] = c; m[1, 2] = -s
    m[2, 1] = s; m[2, 2] = c
    return m


def rotate_y(deg: float) -> np.ndarray:
    a = np.radians(deg); c = np.cos(a); s = np.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = c;  m[0, 2] = s
    m[2, 0] = -s; m[2, 2] = c
    return m


def rotate_z(deg: float) -> np.ndarray:
    a = np.radians(deg); c = np.cos(a); s = np.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = c; m[0, 1] = -s
    m[1, 0] = s; m[1, 1] = c
    return m


def perspective(fov_deg: float, aspect: float, near: float, far: float) -> np.ndarray:
    f = 1.0 / np.tan(np.radians(fov_deg) * 0.5)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def ortho(left: float, right: float, bottom: float, top: float,
          near: float, far: float) -> np.ndarray:
    m = np.eye(4, dtype=np.float32)
    m[0, 0] = 2.0 / (right - left)
    m[1, 1] = 2.0 / (top - bottom)
    m[2, 2] = -2.0 / (far - near)
    m[0, 3] = -(right + left) / (right - left)
    m[1, 3] = -(top + bottom) / (top - bottom)
    m[2, 3] = -(far + near) / (far - near)
    return m


def look_at(eye, target, up) -> np.ndarray:
    e = np.array(eye, dtype=np.float32)
    t = np.array(target, dtype=np.float32)
    u = np.array(up, dtype=np.float32)

    f = t - e
    nf = float(np.linalg.norm(f))
    if nf < 1e-8:
        # Cámara degenerada: eye == target. Devolvemos identidad
        # (equivalente a una cámara mirando hacia -Z desde el origen).
        return np.eye(4, dtype=np.float32)
    f = f / nf

    s = np.cross(f, u)
    ns = float(np.linalg.norm(s))
    if ns < 1e-8:
        # up paralelo a forward: no se puede construir base. Identidad.
        return np.eye(4, dtype=np.float32)
    s = s / ns

    up2 = np.cross(s, f)

    m = np.eye(4, dtype=np.float32)
    m[0, :3] = s;   m[0, 3] = -np.dot(s, e)
    m[1, :3] = up2; m[1, 3] = -np.dot(up2, e)
    m[2, :3] = -f;  m[2, 3] =  np.dot(f, e)
    return m
