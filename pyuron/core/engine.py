import pygame

from pyuron.audio.audio_manager import AudioManager
from pyuron.core.config import EngineConfig
from pyuron.core.logger import Log
from pyuron.core.timing import Timer, timed
from pyuron.core.window import Window
from pyuron.graphics.renderer import Renderer
from pyuron.input.input_manager import InputManager
from pyuron.resources.assets import AssetManager
from pyuron.scene.scene import Scene


class Engine:
    MAX_FIXED_STEPS = 8

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self.window: Window | None = None
        self.renderer: Renderer | None = None
        self.scene: Scene | None = None
        self._pending_scene: Scene | None = None
        
        # Subsistemas
        self.input = InputManager()
        self.audio = AudioManager()
        self.assets = AssetManager()  # ← Ahora el motor gestiona los recursos
        
        self.is_running = False
        self._closed = False
        self.delta_time = 0.0
        self._clock = pygame.time.Clock()

        self._on_update: list = []
        self._on_render: list = []
        self._on_resize: list = []

        self._fps_window_s = 2.0
        self._fps_elapsed  = 0.0
        self._fps_frames   = 0
        self._draw_ms_accum = 0.0

        self.fixed_dt = self.config.fixed_dt
        self._accumulator = 0.0

    # ── API pública ─────────────────────────────────────────────────
    def set_scene(self, scene: Scene) -> None:
        """Encola un cambio de escena. Se aplicará al inicio del siguiente frame."""
        self._pending_scene = scene

    def _apply_pending_scene(self) -> None:
        """Aplica el cambio de escena pendiente con ciclo de vida correcto."""
        if self._pending_scene is None:
            return
        if self.scene is not None:
            self.scene._exit_tree_recursive()
            Log.info(f"Escena saliente: {self.scene.name}")
        self.scene = self._pending_scene
        self.scene._enter_tree_recursive()
        Log.ok(f"Escena entrante: {self.scene.name}")
        self._pending_scene = None

    def on_update(self, fn) -> None: self._on_update.append(fn)
    def on_render(self, fn) -> None: self._on_render.append(fn)
    def on_resize(self, fn) -> None: self._on_resize.append(fn)

    # ── Ciclo de vida ───────────────────────────────────────────────
    def initialize(self) -> None:
        if self.window is not None:
            return
        try:
            self._do_initialize()
        except Exception as e:
            Log.err(f"Fallo crítico durante la inicialización: {e}")
            self.shutdown()
            raise

    def _do_initialize(self) -> None:
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

        with timed("Inicialización audio"):
            self.audio.init()

        Log.time("Arranque total", startup.elapsed_ms)
        Log.divider()

    def _compute_steps(self, dt: float) -> list[float]:
        if self.fixed_dt is None:
            return [dt]
        self._accumulator += dt
        steps = int(self._accumulator / self.fixed_dt)
        if steps >= self.MAX_FIXED_STEPS:
            self._accumulator = 0.0
            steps = self.MAX_FIXED_STEPS
        else:
            self._accumulator -= steps * self.fixed_dt
        return [self.fixed_dt] * steps

    def _update(self, dt: float) -> None:
        for fn in self._on_update:
            fn(dt)
        if self.scene is not None:
            self.scene._process(dt)

    def _render_frame(self) -> None:
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

    def run(self) -> None:
        self.initialize()
        self._apply_pending_scene()
        self.is_running = True
        try:
            while self.is_running:
                self._apply_pending_scene()
                self.delta_time = self._clock.tick() / 1000.0
                self._process_events()
                if not self.is_running:
                    break
                steps = self._compute_steps(self.delta_time)
                for step_dt in steps:
                    self._update(step_dt)
                self._apply_pending_scene()
                self._render_frame()
                self._report_fps()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            Log.err(f"Excepción en el bucle principal: {e}")
            raise
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
        Log.metrics(f"FPS {fps:5.1f}  ·  frame {frame_ms:5.2f} ms  ·  draw {draw_ms:5.2f} ms")
        self._fps_elapsed = 0.0
        self._fps_frames = 0
        self._draw_ms_accum = 0.0

    def stop(self) -> None:
        self.is_running = False

    def shutdown(self) -> None:
        if getattr(self, "_closed", False):
            return
        self.is_running = False

        try:
            self.audio.shutdown()
        except Exception as e:
            Log.warn(f"Error cerrando audio: {e}")

        # Liberar recursos GPU (VAO, VBO, Texturas, Shaders)
        try:
            self.assets.dispose_all()
        except Exception as e:
            Log.warn(f"Error liberando recursos GPU: {e}")

        window_was_initialized = self.window is not None
        try:
            if self.window is not None:
                self.window.close()
                self.window = None
        except Exception as e:
            Log.warn(f"Error cerrando ventana: {e}")

        self.renderer = None

        if window_was_initialized:
            try:
                pygame.quit()
            except Exception:
                pass

        self._closed = True
        Log.info("Motor detenido. Hasta pronto.")
