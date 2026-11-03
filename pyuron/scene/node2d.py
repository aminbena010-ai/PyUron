from pyuron.scene.node import Node
from pyuron.math.transform import Transform


class Node2D(Node):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.transform = Transform()
