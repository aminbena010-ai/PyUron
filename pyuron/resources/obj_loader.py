"""Parser OBJ minimalista (v, vn, vt, f). Devuelve (vertices, indices)."""
from __future__ import annotations

from pathlib import Path

import numpy as np


def load_obj(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (vertices, indices).

    vertices: array (N, 8) float32 → (x,y,z, nx,ny,nz, u,v)
    indices:  array (M,) uint32
    """
    positions: list[tuple[float, float, float]] = []
    normals:   list[tuple[float, float, float]] = []
    uvs:       list[tuple[float, float]] = []
    faces:     list[list[tuple[int, int, int]]] = []

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        tag = parts[0]

        if tag == "v":
            positions.append(tuple(map(float, parts[1:4])))
        elif tag == "vn":
            normals.append(tuple(map(float, parts[1:4])))
        elif tag == "vt":
            uvs.append(tuple(map(float, parts[1:3])))
        elif tag == "f":
            face: list[tuple[int, int, int]] = []
            for token in parts[1:]:
                bits = token.split("/")
                v_idx  = int(bits[0]) - 1
                vt_idx = int(bits[1]) - 1 if len(bits) > 1 and bits[1] else -1
                vn_idx = int(bits[2]) - 1 if len(bits) > 2 and bits[2] else -1
                face.append((v_idx, vt_idx, vn_idx))
            faces.append(face)

    # Deduplicar (v_idx, vt_idx, vn_idx) y construir array de vértices.
    unique: dict[tuple[int, int, int], int] = {}
    vertices: list[tuple[float, ...]] = []
    indices: list[int] = []

    for face in faces:
        for key in face:
            if key not in unique:
                unique[key] = len(vertices)
                v_idx, vt_idx, vn_idx = key
                px, py, pz = positions[v_idx]
                nx, ny, nz = normals[vn_idx] if vn_idx >= 0 and vn_idx < len(normals) else (0.0, 1.0, 0.0)
                u, v = uvs[vt_idx] if vt_idx >= 0 and vt_idx < len(uvs) else (0.0, 0.0)
                vertices.append((px, py, pz, nx, ny, nz, u, v))
            indices.append(unique[key])

    # Triangulación en abanico para caras con >3 vértices.
    if any(len(face) > 3 for face in faces):
        indices = []
        unique = {}
        vertices = []
        for face in faces:
            # Fan-triangulate
            for i in range(1, len(face) - 1):
                tri = [face[0], face[i], face[i + 1]]
                for key in tri:
                    if key not in unique:
                        unique[key] = len(vertices)
                        v_idx, vt_idx, vn_idx = key
                        px, py, pz = positions[v_idx]
                        nx, ny, nz = normals[vn_idx] if vn_idx >= 0 and vn_idx < len(normals) else (0.0, 1.0, 0.0)
                        u, v = uvs[vt_idx] if vt_idx >= 0 and vt_idx < len(uvs) else (0.0, 0.0)
                        vertices.append((px, py, pz, nx, ny, nz, u, v))
                    indices.append(unique[key])

    return (
        np.asarray(vertices, dtype=np.float32),
        np.asarray(indices,  dtype=np.uint32),
    )
