"""AnimatedSprite2D: spritesheet en grid con fps, loop y ping-pong."""
from __future__ import annotations

from typing import Literal

from pyuron.graphics.shader import Shader
from pyuron.graphics.texture import Texture2D
from pyuron.scene.sprite2d import Sprite2D


LoopMode = Literal["loop", "once", "ping_pong"]


class AnimatedSprite2D(Sprite2D):
    def __init__(
        self,
        texture: Texture2D,
        shader: Shader,
        frame_w: int,
        frame_h: int,
        name: str = "AnimatedSprite2D",
    ) -> None:
        super().__init__(texture, shader, name)
        if frame_w <= 0 or frame_h <= 0:
            raise ValueError("frame_w y frame_h deben ser positivos.")
        if frame_w > texture.width or frame_h > texture.height:
            raise ValueError("El frame es más grande que la textura.")

        self.frame_w = frame_w
        self.frame_h = frame_h
        self.frames_x = texture.width // frame_w
        self.frames_y = texture.height // frame_h
        if self.frames_x <= 0 or self.frames_y <= 0:
            raise ValueError("La textura no contiene ningún frame del tamaño dado.")

        self.frame_count = self.frames_x * self.frames_y
        self.current_frame = 0
        self.fps = 10.0
        self.playing = True
        self.loop_mode: LoopMode = "loop"
        self._time_accum = 0.0
        self._direction = 1  # para ping_pong

    # ── API ────────────────────────────────────────────────────────
    def play(self) -> None:
        self.playing = True

    def stop(self) -> None:
        self.playing = False
        self.current_frame = 0
        self._time_accum = 0.0
        self._direction = 1

    def pause(self) -> None:
        self.playing = False

    def goto(self, frame: int) -> None:
        self.current_frame = max(0, min(self.frame_count - 1, frame))
        self._time_accum = 0.0

    # ── Update ─────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        if not self.playing or self.fps <= 0.0 or self.frame_count <= 1:
            return

        frame_dur = 1.0 / self.fps
        self._time_accum += dt
        while self._time_accum >= frame_dur:
            self._time_accum -= frame_dur
            self._advance()

    def _advance(self) -> None:
        if self.loop_mode == "loop":
            self.current_frame = (self.current_frame + 1) % self.frame_count
        elif self.loop_mode == "once":
            if self.current_frame < self.frame_count - 1:
                self.current_frame += 1
            else:
                self.playing = False
        elif self.loop_mode == "ping_pong":
            self.current_frame += self._direction
            if self.current_frame >= self.frame_count - 1:
                self.current_frame = self.frame_count - 1
                self._direction = -1
            elif self.current_frame <= 0:
                self.current_frame = 0
                self._direction = 1

    # ── UV rect del frame actual ───────────────────────────────────
    def uv_rect(self) -> tuple[float, float, float, float]:
        col = self.current_frame % self.frames_x
        row = self.current_frame // self.frames_x
        u = col / self.frames_x
        v = row / self.frames_y
        w = 1.0 / self.frames_x
        h = 1.0 / self.frames_y
        return (u, v, w, h)
