import pygame

from pyuron.core.config import EngineConfig
from pyuron.core.logger import Log
from pyuron.core.timing import Timer, timed
from pyuron.core.window import Window
from pyuron.graphics.renderer import Renderer
from pyuron.scene.scene import Scene


class Engine:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.window: Window | None = None
        self.renderer: Renderer | None = None
        self.scene: Scene | None = None
        self.is_running = False
        self.delta_time = 0.0
        self._clock = pygame.time.Clock()

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

        startup = Timer()
        Log.header("Arranque de PyUron")

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

        Log.time("Arranque total", startup.elapsed_ms)
        Log.divider()

    def run(self) -> None:
        self.initialize()
        self.is_running = True

        try:
            while self.is_running:
                self.delta_time = self._clock.tick() / 1000.0
                self._process_events()
                if not self.is_running:
                    break

                # 1) Update
                for fn in self._on_update:
                    fn(self.delta_time)
                if self.scene is not None:
                    self.scene._process(self.delta_time)

                # 2) Render
                assert self.renderer is not None and self.window is not None
                self.renderer.begin_frame()

                for fn in self._on_render:
                    fn()

                if self.scene is not None:
                    t = Timer()
                    self.scene.render(self.renderer)
                    self._draw_ms_accum += t.elapsed_ms

                self.renderer.end_frame()
                self.window.swap_buffers()

                self._report_fps()
        except KeyboardInterrupt:
            self.stop()
        finally:
            self.shutdown()

    def _process_events(self) -> None:
        for event in pygame.event.get():
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
        self.is_running = False
        if self.window is not None:
            self.window.close()
            self.window = None
        self.renderer = None
        pygame.quit()
        Log.info("Motor detenido. Hasta pronto.")
