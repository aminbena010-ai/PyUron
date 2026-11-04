import numpy as np
import pytest
from pathlib import Path

from pyuron.resources.obj_loader import load_obj


def test_cube_obj_loads():
    path = Path("assets/models/cube.obj")
    assert path.exists(), "El cubo.obj debe existir en assets/models/"

    vertices, indices = load_obj(path)
    assert vertices.shape[1] == 8   # pos(3) + normal(3) + uv(2)
    assert indices.ndim == 1
    assert len(indices) == 36       # 12 triángulos × 3
    assert vertices.dtype == np.float32
    assert indices.dtype == np.uint32


def test_cube_has_36_indices():
    _, indices = load_obj("assets/models/cube.obj")
    # 6 caras × 2 triángulos × 3 vértices = 36
    assert len(indices) == 36


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_obj("assets/models/nope.obj")
