import pygame

from pyuron.audio.audio_manager import AudioManager
from pyuron.core.config import EngineConfig
from pyuron.core.logger import Log
from pyuron.core.timing import Timer, timed
from pyuron.core.window import Window
from pyuron.graphics.renderer import Renderer
from pyuron.input.input_manager import InputManager
from pyuron.scene.scene import Scene


class Engine:
    # Límite de pasos fijos por frame para evitar la "espiral de la muerte".
    MAX_FIXED_STEPS = 8

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.window: Window | None = None
        self.renderer: Renderer | None = None
        self.scene: Scene | None = None
        self.input = InputManager()
        self.audio = AudioManager()
        self.is_running = False
        self.delta_time = 0.0
        self._clock = pygame.time.Clock()
        self._accumulator = 0.0
        self._pygame_started = False
        self._closed = False

        self._on_update: list = []
        self._on_render: list = []
        self._on_resize: list = []

        self._fps_window_s = 2.0
        self._fps_elapsed  = 0.0
        self._fps_frames   = 0
        self._draw_ms_accum = 0.0

    # ── API pública ─────────────────────────────────────────────────
    def set_scene(self, scene: Scene) -> None:
        self.scene = scene
        Log.ok(f"Escena cargada: {scene.name}")

    def on_update(self, fn) -> None: self._on_update.append(fn)
    def on_render(self, fn) -> None: self._on_render.append(fn)
    def on_resize(self, fn) -> None: self._on_resize.append(fn)

    # ── Ciclo de vida ───────────────────────────────────────────────
    def initialize(self) -> None:
        if self.window is not None:
            return

        self._closed = False
        self._pygame_started = True

        startup = Timer()
        Log.header("Arranque de PyUron")

        try:
            with timed("Inicialización ventana"):
                self.window = Window(
                    title=self.config.title,
                    width=self.config.width,
                    height=self.config.height,
                    resizable=self.config.resizable,
                    vsync=self.config.vsync,
                    gl_major=self.config.gl_major,
                    gl_minor=self.config.gl_minor,
                )
            Log.ok(f"Ventana creada ({self.config.width}×{self.config.height})")

            with timed("Inicialización renderer / contexto GL"):
                self.renderer = Renderer(
                    self.config.width, self.config.height, self.config.clear_color,
                )
            Log.ok(f"OpenGL {self.renderer.version}")
        except BaseException:
            self.shutdown()
            raise

        with timed("Inicialización audio"):
            self.audio.init()

        Log.time("Arranque total", startup.elapsed_ms)
        Log.divider()

    def _compute_steps(self, frame_dt: float) -> list[float]:
        """Divide el frame en pasos de simulación.

        Sin `fixed_dt` devuelve `[frame_dt]` (comportamiento 1.0.0). Con
        `fixed_dt` acumula y devuelve pasos constantes, limitando el número
        de pasos por frame y descartando el excedente si se supera el límite.
        """
        fixed = self.config.fixed_dt
        if fixed is None:
            return [frame_dt]

        self._accumulator += max(0.0, frame_dt)
        steps: list[float] = []
        while self._accumulator >= fixed and len(steps) < self.MAX_FIXED_STEPS:
            steps.append(fixed)
            self._accumulator -= fixed
        if len(steps) >= self.MAX_FIXED_STEPS:
            self._accumulator = 0.0
        return steps

    def _update(self, dt: float) -> None:
        """Actualización lógica de un paso. No requiere ventana ni GL."""
        for fn in self._on_update:
            fn(dt)
        if self.scene is not None:
            self.scene._process(dt)

    def _render_frame(self) -> None:
        if self.renderer is None or self.window is None:
            raise RuntimeError(
                "El motor no está inicializado: falta ventana o renderer."
            )

        self.renderer.begin_frame()
        for fn in self._on_render:
            fn()
        if self.scene is not None:
            t = Timer()
            self.scene.render(self.renderer)
            self._draw_ms_accum += t.elapsed_ms
        self.renderer.end_frame()
        self.window.swap_buffers()

    def run(self) -> None:
        self.initialize()
        self.is_running = True

        try:
            while self.is_running:
                frame_dt = self._clock.tick() / 1000.0
                self.delta_time = frame_dt
                self._process_events()
                if not self.is_running:
                    break

                for dt in self._compute_steps(frame_dt):
                    self._update(dt)

                self._render_frame()
                self._report_fps()
        except KeyboardInterrupt:
            self.stop()
        finally:
            self.shutdown()

    def _process_events(self) -> None:
        self.input.begin_frame()
        for event in pygame.event.get():
            self.input.process_event(event)
            if event.type == pygame.QUIT:
                self.stop()
            elif event.type in (pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED):
                w = getattr(event, "w", None) or getattr(event, "x", None)
                h = getattr(event, "h", None) or getattr(event, "y", None)
                if w is None or h is None:
                    continue
                if self.window is not None:
                    self.window.set_size(w, h)
                if self.renderer is not None:
                    self.renderer.resize(w, h)
                for fn in self._on_resize:
                    fn(w, h)

    def _report_fps(self) -> None:
        self._fps_elapsed += self.delta_time
        self._fps_frames += 1
        if self._fps_elapsed < self._fps_window_s:
            return
        fps = self._fps_frames / self._fps_elapsed if self._fps_elapsed > 0 else 0.0
        frame_ms = (self._fps_elapsed / self._fps_frames) * 1000.0 if self._fps_frames else 0.0
        draw_ms = self._draw_ms_accum / self._fps_frames if self._fps_frames else 0.0
        Log.metrics(
            f"FPS {fps:5.1f}  ·  frame {frame_ms:5.2f} ms  ·  draw {draw_ms:5.2f} ms"
        )
        self._fps_elapsed = 0.0
        self._fps_frames = 0
        self._draw_ms_accum = 0.0

    def stop(self) -> None:
        self.is_running = False

    def shutdown(self) -> None:
        """Libera los recursos propios del motor. Es idempotente."""
        if self._closed:
            return
        self._closed = True
        self.is_running = False

        self.audio.shutdown()

        if self.renderer is not None:
            from pyuron.graphics.sprite_quad import dispose_sprite_quad

            dispose_sprite_quad()
            self.renderer = None

        if self.window is not None:
            self.window.close()
            self.window = None

        if self._pygame_started:
            pygame.quit()
            self._pygame_started = False

        Log.info("Motor detenido. Hasta pronto.")
