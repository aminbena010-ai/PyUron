"""Nodo base con jerarquía padre-hijo."""
from __future__ import annotations


class Node:
    def __init__(self, name: str = "") -> None:
        self.name = name or self.__class__.__name__
        self.parent: "Node | None" = None
        self.children: list["Node"] = []
        self.visible = True

    def add_child(self, child: "Node") -> "Node":
        if child.parent is not None:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: "Node") -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    # Subclases sobrescriben esto.
    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def _process(self, dt: float) -> None:
        self.update(dt)
        for child in list(self.children):
            child._process(dt)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
