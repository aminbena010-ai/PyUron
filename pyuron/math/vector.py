"""Vectores ligeros basados en numpy."""
from __future__ import annotations

import numpy as np


class Vector2:
    __slots__ = ("_data",)

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self._data = np.array([float(x), float(y)], dtype=np.float32)

    @property
    def x(self) -> float: return float(self._data[0])

    @x.setter
    def x(self, v: float) -> None: self._data[0] = float(v)

    @property
    def y(self) -> float: return float(self._data[1])

    @y.setter
    def y(self, v: float) -> None: self._data[1] = float(v)

    def to_array(self) -> np.ndarray:
        return self._data.copy()

    def __add__(self, o: "Vector2") -> "Vector2":
        return Vector2(self.x + o.x, self.y + o.y)

    def __sub__(self, o: "Vector2") -> "Vector2":
        return Vector2(self.x - o.x, self.y - o.y)

    def __mul__(self, s: float) -> "Vector2":
        return Vector2(self.x * s, self.y * s)

    __rmul__ = __mul__

    def length(self) -> float:
        return float(np.linalg.norm(self._data))

    def __repr__(self) -> str:
        return f"Vector2({self.x}, {self.y})"


class Vector3:
    __slots__ = ("_data",)

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self._data = np.array([float(x), float(y), float(z)], dtype=np.float32)

    @property
    def x(self) -> float: return float(self._data[0])

    @x.setter
    def x(self, v: float) -> None: self._data[0] = float(v)

    @property
    def y(self) -> float: return float(self._data[1])

    @y.setter
    def y(self, v: float) -> None: self._data[1] = float(v)

    @property
    def z(self) -> float: return float(self._data[2])

    @z.setter
    def z(self, v: float) -> None: self._data[2] = float(v)

    def to_array(self) -> np.ndarray:
        return self._data.copy()

    def __add__(self, o: "Vector3") -> "Vector3":
        return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: "Vector3") -> "Vector3":
        return Vector3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s: float) -> "Vector3":
        return Vector3(self.x * s, self.y * s, self.z * s)

    __rmul__ = __mul__

    def __truediv__(self, s: float) -> "Vector3":
        if s == 0:
            raise ZeroDivisionError("División por cero en Vector3")
        return Vector3(self.x / s, self.y / s, self.z / s)

    def __neg__(self) -> "Vector3":
        return Vector3(-self.x, -self.y, -self.z)

    def length(self) -> float:
        return float(np.linalg.norm(self._data))

    def normalized(self) -> "Vector3":
        n = self.length()
        if n == 0.0:
            return Vector3()
        return Vector3(self.x / n, self.y / n, self.z / n)

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, d: dict) -> "Vector3":
        return cls(float(d.get("x", 0.0)),
                   float(d.get("y", 0.0)),
                   float(d.get("z", 0.0)))

    def __repr__(self) -> str:
        return f"Vector3({self.x}, {self.y}, {self.z})"
