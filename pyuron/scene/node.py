"""Nodo base con jerarquía padre-hijo."""
from __future__ import annotations


class Node:
    """Nodo base con jerarquía padre-hijo.

    Invariantes:
      - Un nodo tiene como máximo un padre y no puede ser ancestro de sí mismo.
      - `add_child` reparenta un nodo ya enlazado y rechaza ciclos.
      - `_process` recorre una copia de la lista de hijos. Un hijo añadido por
        un nodo ya recorrido (p. ej. un hermano) se procesa en el siguiente
        frame; el añadido por el propio nodo antes de recorrer sus hijos se
        procesa en el mismo frame. Un hijo eliminado tras tomarse la copia
        todavía puede procesarse en el frame en curso.
    """

    def __init__(self, name: str = "") -> None:
        self.name = name or self.__class__.__name__
        self.parent: "Node | None" = None
        self.children: list["Node"] = []
        self.visible = True

    def add_child(self, child: "Node") -> "Node":
        node: "Node | None" = self
        while node is not None:
            if node is child:
                raise ValueError(
                    f"No se puede añadir '{child.name}' como hijo de "
                    f"'{self.name}': crearía un ciclo en la jerarquía."
                )
            node = node.parent

        if child.parent is not None:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child: "Node") -> bool:
        """Desenlaza `child` si es hijo directo. Devuelve si se eliminó."""
        if child.parent is self and child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False

    # Subclases sobrescriben esto.
    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def _process(self, dt: float) -> None:
        self.update(dt)
        for child in list(self.children):
            child._process(dt)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
