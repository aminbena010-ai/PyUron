from pyuron.math.transform import Transform
from pyuron.math.vector import Vector3
from pyuron.scene.node import Node


class Node3D(Node):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.transform = Transform()

    def world_position(self) -> Vector3:
        """Suma las posiciones de los ancestros. Ignora rotación y escala."""
        pos = Vector3(0, 0, 0)
        node = self
        while node is not None:
            if isinstance(node, Node3D):
                pos = pos + node.transform.position
            node = node.parent
        return pos
