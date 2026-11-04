"""Audio: música y efectos con volumen maestro, fade y tonos procedurales."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pygame

from pyuron.core.logger import Log


class AudioManager:
    """Servicio de audio centralizado.

    Uso básico:
        audio = AudioManager()
        audio.init()                          # opcional, se llama al cargar 1er sonido
        audio.play_music("assets/music/theme.ogg", loops=-1)
        audio.play_sfx("assets/sfx/click.wav")
    """

    def __init__(self) -> None:
        self._initialized = False
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}

        self._master_volume = 1.0
        self._music_volume  = 0.6
        self._sfx_volume    = 1.0

    # ── Inicialización perezosa ─────────────────────────────────────
    def init(self) -> bool:
        """Inicializa pygame.mixer. Devuelve True si tuvo éxito."""
        if self._initialized:
            return True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            self._initialized = True
            Log.ok("Audio inicializado")
            return True
        except pygame.error as e:
            Log.warn(f"No se pudo inicializar el audio: {e}")
            return False

    # ── Volumen ─────────────────────────────────────────────────────
    def set_master_volume(self, v: float) -> None:
        self._master_volume = max(0.0, min(1.0, float(v)))
        if self._initialized:
            pygame.mixer.music.set_volume(self._master_volume * self._music_volume)

    def set_music_volume(self, v: float) -> None:
        self._music_volume = max(0.0, min(1.0, float(v)))
        if self._initialized:
            pygame.mixer.music.set_volume(self._master_volume * self._music_volume)

    def set_sfx_volume(self, v: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, float(v)))

    @property
    def master_volume(self) -> float:
        return self._master_volume

    # ── SFX ─────────────────────────────────────────────────────────
    def load_sfx(self, path: str | Path) -> pygame.mixer.Sound | None:
        if not self._initialized and not self.init():
            return None
        key = str(path)
        if key not in self._sfx_cache:
            try:
                self._sfx_cache[key] = pygame.mixer.Sound(key)
            except (pygame.error, FileNotFoundError) as e:
                Log.warn(f"No se pudo cargar sonido {path}: {e}")
                return None
        return self._sfx_cache[key]

    def play_sfx(
        self,
        sound_or_path: pygame.mixer.Sound | str | Path,
        volume: float = 1.0,
        loops: int = 0,
    ) -> pygame.mixer.Channel | None:
        if not self._initialized and not self.init():
            return None

        if isinstance(sound_or_path, (str, Path)):
            sound = self.load_sfx(sound_or_path)
        else:
            sound = sound_or_path
        if sound is None:
            return None

        channel = pygame.mixer.find_channel(True)
        if channel is None:
            return None
        channel.set_volume(max(0.0, min(1.0, volume)) * self._master_volume * self._sfx_volume)
        channel.play(sound, loops=loops)
        return channel

    def register_sound(self, name: str, sound: pygame.mixer.Sound) -> None:
        """Registra un sonido ya creado (por ejemplo, procedural)."""
        self._sfx_cache[name] = sound

    # ── Música ──────────────────────────────────────────────────────
    def play_music(
        self, path: str | Path, loops: int = -1, fade_ms: int = 0,
    ) -> None:
        if not self._initialized and not self.init():
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._master_volume * self._music_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        except (pygame.error, FileNotFoundError) as e:
            Log.warn(f"No se pudo reproducir música {path}: {e}")

    def stop_music(self, fade_ms: int = 0) -> None:
        if self._initialized:
            pygame.mixer.music.fadeout(fade_ms) if fade_ms else pygame.mixer.music.stop()

    def pause_music(self) -> None:
        if self._initialized:
            pygame.mixer.music.pause()

    def resume_music(self) -> None:
        if self._initialized:
            pygame.mixer.music.unpause()

    # ── Shutdown ────────────────────────────────────────────────────
    def shutdown(self) -> None:
        if self._initialized:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
            pygame.mixer.quit()
            self._initialized = False


# ── Tonos procedurales (no requiere archivos) ─────────────────────
def make_tone(
    frequency: float = 440.0,
    duration: float = 0.1,
    sample_rate: int = 44100,
    volume: float = 0.3,
) -> pygame.mixer.Sound:
    """Genera un tono senoidal como Sound de pygame."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    frames = int(sample_rate * duration)
    t = np.arange(frames) / sample_rate
    wave = np.sin(2 * np.pi * frequency * t)
    # Aplicar fade-in/out para evitar clics
    fade = int(sample_rate * 0.01)
    if fade < frames:
        wave[:fade] *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)
    samples = (wave * 32767 * volume).astype(np.int16)
    stereo = np.column_stack([samples, samples])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))
