"""Sistema de input con mapeo de acciones.

Uso:
    inp = InputManager()
    inp.bind_action("jump",  pygame.K_SPACE)
    inp.bind_action("left",  pygame.K_a, pygame.K_LEFT)
    inp.bind_action("fire",  pygame.BUTTON_LEFT)  # botón de ratón

    # Cada frame:
    inp.begin_frame()
    for event in pygame.event.get():
        inp.process_event(event)

    if inp.is_action_just_pressed("jump"):
        ...
"""
from __future__ import annotations

import pygame


class InputManager:
    def __init__(self) -> None:
        self._actions: dict[str, tuple[int, ...]] = {}

        self._keys_down: set[int] = set()
        self._keys_pressed_frame: set[int] = set()
        self._keys_released_frame: set[int] = set()

        self._mouse_buttons_down: set[int] = set()
        self._mouse_buttons_pressed_frame: set[int] = set()
        self._mouse_buttons_released_frame: set[int] = set()

        self._mouse_pos: tuple[int, int] = (0, 0)
        self._mouse_delta: tuple[int, int] = (0, 0)
        self._mouse_wheel: int = 0

    # ── Configuración ───────────────────────────────────────────────
    def bind_action(self, name: str, *keys: int) -> None:
        """Asocia uno o más keycodes/botones a una acción."""
        self._actions[name] = tuple(keys)

    def unbind_action(self, name: str) -> None:
        self._actions.pop(name, None)

    # ── Ciclo por frame ─────────────────────────────────────────────
    def begin_frame(self) -> None:
        """Limpia el estado 'de este frame'. Llamar al inicio del frame."""
        self._keys_pressed_frame.clear()
        self._keys_released_frame.clear()
        self._mouse_buttons_pressed_frame.clear()
        self._mouse_buttons_released_frame.clear()
        self._mouse_delta = (0, 0)
        self._mouse_wheel = 0

    def process_event(self, event: pygame.event.Event) -> None:
        """Procesa un evento de pygame y actualiza el estado."""
        if event.type == pygame.KEYDOWN:
            if event.key not in self._keys_down:
                self._keys_pressed_frame.add(event.key)
            self._keys_down.add(event.key)
        elif event.type == pygame.KEYUP:
            self._keys_down.discard(event.key)
            self._keys_released_frame.add(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_buttons_down.add(event.button)
            self._mouse_buttons_pressed_frame.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_buttons_down.discard(event.button)
            self._mouse_buttons_released_frame.add(event.button)
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos
            self._mouse_delta = event.rel
        elif event.type == pygame.MOUSEWHEEL:
            self._mouse_wheel += event.y

    # ── Consultas de acción ─────────────────────────────────────────
    def is_action_pressed(self, name: str) -> bool:
        keys = self._actions.get(name, ())
        return any(k in self._keys_down or k in self._mouse_buttons_down
                   for k in keys)

    def is_action_just_pressed(self, name: str) -> bool:
        keys = self._actions.get(name, ())
        return any(k in self._keys_pressed_frame
                   or k in self._mouse_buttons_pressed_frame for k in keys)

    def is_action_just_released(self, name: str) -> bool:
        keys = self._actions.get(name, ())
        return any(k in self._keys_released_frame
                   or k in self._mouse_buttons_released_frame for k in keys)

    # ── Consultas de teclas / ratón ─────────────────────────────────
    def is_key_pressed(self, key: int) -> bool:
        return key in self._keys_down

    def is_mouse_button_pressed(self, button: int) -> bool:
        return button in self._mouse_buttons_down

    @property
    def mouse_pos(self) -> tuple[int, int]:
        return self._mouse_pos

    @property
    def mouse_delta(self) -> tuple[int, int]:
        return self._mouse_delta

    @property
    def mouse_wheel(self) -> int:
        return self._mouse_wheel

    # ── Utilidades ──────────────────────────────────────────────────
    def get_vector_2d(
        self,
        up: str, down: str, left: str, right: str,
    ) -> tuple[float, float]:
        """Devuelve (x, y) normalizado según 4 acciones de movimiento."""
        x = (1.0 if self.is_action_pressed(right) else 0.0) - \
            (1.0 if self.is_action_pressed(left)  else 0.0)
        y = (1.0 if self.is_action_pressed(up)    else 0.0) - \
            (1.0 if self.is_action_pressed(down)  else 0.0)
        length = (x * x + y * y) ** 0.5
        if length > 0:
            x /= length
            y /= length
        return (x, y)
