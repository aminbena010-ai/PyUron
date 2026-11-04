from pyuron.scene.node import Node
from pyuron.math.transform import Transform


class Node3D(Node):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.transform = Transform()

    def world_position(self):
        from pyuron.math.vector import Vector3
        pos = Vector3(0, 0, 0)
        node = self
        while node is not None:
            if isinstance(node, Node3D):
                pos = pos + node.transform.position
            node = node.parent
        return pos
