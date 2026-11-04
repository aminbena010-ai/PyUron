"""Timers de gameplay: Cooldown y Stopwatch."""
from __future__ import annotations


class Cooldown:
    """Cooldown para fire-rate, invencibilidad, etc.

    Uso:
        cd = Cooldown(0.2)
        # en update:
        cd.update(dt)
        if cd.trigger():  # devuelve True y reinicia
            shoot()
    """

    __slots__ = ("duration", "_remaining")

    def __init__(self, duration: float) -> None:
        if duration < 0:
            raise ValueError("duration debe ser >= 0")
        self.duration = float(duration)
        self._remaining = 0.0

    def update(self, dt: float) -> None:
        if self._remaining > 0:
            self._remaining = max(0.0, self._remaining - dt)

    def trigger(self) -> bool:
        """Si está listo, reinicia y devuelve True. Si no, False."""
        if self._remaining <= 0:
            self._remaining = self.duration
            return True
        return False

    def reset(self) -> None:
        self._remaining = self.duration

    @property
    def ready(self) -> bool:
        return self._remaining <= 0

    @property
    def remaining(self) -> float:
        return self._remaining

    @property
    def progress(self) -> float:
        """0 = recién disparado, 1 = listo."""
        if self.duration <= 0:
            return 1.0
        return 1.0 - (self._remaining / self.duration)


class Stopwatch:
    """Cuenta hacia arriba desde 0. Útil para vidas, buffers, etc."""

    __slots__ = ("_elapsed",)

    def __init__(self) -> None:
        self._elapsed = 0.0

    def update(self, dt: float) -> None:
        self._elapsed += dt

    def reset(self) -> None:
        self._elapsed = 0.0

    @property
    def elapsed(self) -> float:
        return self._elapsed
