"""Utilidades de medición de tiempo para PyUron."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from pyuron.core.logger import Log


class Timer:
    """Cronómetro de alta resolución basado en perf_counter."""

    __slots__ = ("_start",)

    def __init__(self) -> None:
        self._start = time.perf_counter()

    def reset(self) -> None:
        self._start = time.perf_counter()

    @property
    def elapsed_ms(self) -> float:
        return (time.perf_counter() - self._start) * 1000.0


@contextmanager
def timed(label: str, log: bool = True) -> Iterator[Timer]:
    """Context manager que mide y muestra el bloque con [Tiempo]."""
    t = Timer()
    try:
        yield t
    finally:
        if log:
            Log.time(label, t.elapsed_ms)
