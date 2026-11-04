"""Nodo base con jerarquía padre-hijo y ciclo de vida."""
from __future__ import annotations


class Node:
    def __init__(self, name: str = "") -> None:
        self.name = name or self.__class__.__name__
        self.parent: "Node | None" = None
        self.children: list["Node"] = []
        self.visible = True
        self._in_tree = False

    # ── Ciclo de vida ───────────────────────────────────────────────
    def on_enter_tree(self) -> None:
        """Se llama cuando el nodo entra en el árbol activo (o al añadirse con padre activo)."""

    def on_exit_tree(self) -> None:
        """Se llama cuando el nodo sale del árbol activo (o al eliminarse del padre)."""

    def _enter_tree_recursive(self) -> None:
        if self._in_tree:
            return
        self._in_tree = True
        self.on_enter_tree()
        for child in self.children:
            child._enter_tree_recursive()

    def _exit_tree_recursive(self) -> None:
        if not self._in_tree:
            return
        for child in self.children:
            child._exit_tree_recursive()
        self.on_exit_tree()
        self._in_tree = False

    # ── Jerarquía ──────────────────────────────────────────────────
    def add_child(self, child: "Node") -> "Node":
        # Detección de ciclos: recorremos ancestros. Cubre también el caso
        # "child is self" (añadirse a sí mismo crearía un ciclo trivial).
        node: Node | None = self
        while node is not None:
            if node is child:
                raise ValueError(
                    f"Añadir '{child.name}' como hijo de '{self.name}' crearía un ciclo."
                )
            node = node.parent

        if child.parent is not None:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        # Si el padre ya está en el árbol, el hijo entra inmediatamente
        if self._in_tree:
            child._enter_tree_recursive()
        return child

    def remove_child(self, child: "Node") -> bool:
        if child not in self.children:
            return False
        # Salir del árbol ANTES de desconectar (para que on_exit_tree vea el estado final)
        if self._in_tree:
            child._exit_tree_recursive()
        self.children.remove(child)
        child.parent = None
        return True

    # ── Update ─────────────────────────────────────────────────────
    def update(self, dt: float) -> None:  # noqa: ARG002
        pass

    def _process(self, dt: float) -> None:
        self.update(dt)
        # Copia defensiva: aunque un hijo añada/elimine durante _process, no rompemos el bucle
        for child in list(self.children):
            child._process(dt)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
