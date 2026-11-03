"""Logger de PyUron con símbolos, colores y timestamp.

Default: solo la hora  ->  [18:27:44.123]
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone


RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
GRAY    = "\033[90m"


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("PYURON_NO_COLOR") is not None:
        return False
    return sys.stdout.isatty()


_COLOR = _color_enabled()


def c(color: str, text: str) -> str:
    if not _COLOR:
        return text
    return f"{color}{text}{RESET}"


_DIAS_LARGO = ["lunes", "martes", "miércoles", "jueves",
               "viernes", "sábado", "domingo"]
_DIAS_CORTO = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
_MESES_LARGO = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
_MESES_CORTO = ["ene", "feb", "mar", "abr", "may", "jun",
                "jul", "ago", "sep", "oct", "nov", "dic"]


def _fmt() -> str:
    # ── Por defecto: solo la hora ──
    return (os.environ.get("PYURON_LOG_TIME_FORMAT") or "time").lower()


def _pad() -> str:
    return " " if os.environ.get("PYURON_LOG_TIME_PAD") not in (None, "", "0") else ""


def _sep() -> str:
    return os.environ.get("PYURON_LOG_SEP") or "  "


def _timestamp(fmt: str | None = None) -> str:
    fmt = (fmt or _fmt()).lower()
    now = datetime.now()
    ms = now.microsecond // 1000

    if fmt == "time":
        return f"{now:%H:%M:%S}.{ms:03d}"
    if fmt == "verbose":
        return (f"{_DIAS_LARGO[now.weekday()]}, {now.day:02d} de "
                f"{_MESES_LARGO[now.month - 1]} de {now.year}  ·  "
                f"{now:%H:%M:%S}.{ms:03d}")
    if fmt == "rich":
        s = now.isocalendar().week
        d = now.timetuple().tm_yday
        return (f"{_DIAS_CORTO[now.weekday()]} {now.day:02d} "
                f"{_MESES_CORTO[now.month - 1]} {now.year}  ·  "
                f"S{s:02d}  ·  D{d:03d}  ·  {now:%H:%M:%S}.{ms:03d}")
    if fmt == "full":
        s = now.isocalendar().week
        d = now.timetuple().tm_yday
        return (f"{now:%Y-%m-%d %H:%M:%S}.{ms:03d}  ·  "
                f"semana {s:02d}  ·  día {d:03d}/365")
    if fmt == "iso_utc":
        t = datetime.now(timezone.utc)
        return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"
    if fmt == "date":
        return now.strftime("%Y-%m-%d")
    if fmt == "epoch":
        import time as _t
        return f"{_t.time():.3f}"
    return f"{now:%Y-%m-%d %H:%M:%S}.{ms:03d}"   # iso


def _ts_prefix() -> str:
    fmt = _fmt()
    inner = c(CYAN + BOLD, _timestamp(fmt))
    return c(GRAY, "[") + _pad() + inner + _pad() + c(GRAY, "]")


def _all_lines_get_timestamp() -> bool:
    return os.environ.get("PYURON_LOG_TIMESTAMP") not in (None, "", "0", "false", "False")


def _emit(symbol: str, color: str, msg: str, *, to_stderr: bool = False,
          force_ts: bool = False) -> None:
    parts: list[str] = []
    if force_ts or _all_lines_get_timestamp():
        parts.append(_ts_prefix())
        parts.append(_sep())
    parts.append(c(color, symbol))
    parts.append(msg)
    print("".join(parts), file=(sys.stderr if to_stderr else sys.stdout), flush=True)


class Log:
    @staticmethod
    def ok(msg: str) -> None:
        _emit("[+]", GREEN, msg)

    @staticmethod
    def warn(msg: str) -> None:
        _emit("[!]", YELLOW, msg)

    @staticmethod
    def err(msg: str) -> None:
        _emit("[-]", RED, msg, to_stderr=True)

    @staticmethod
    def info(msg: str) -> None:
        _emit("[?]", CYAN, msg)

    @staticmethod
    def debug(msg: str) -> None:
        if os.environ.get("PYURON_DEBUG") is not None:
            _emit("[.]", GRAY, c(DIM, msg))

    @staticmethod
    def time(label: str, ms: float) -> None:
        unit, val = ("ms", ms)
        if ms >= 1000.0:
            unit, val = "s", ms / 1000.0
        print(
            f"{_ts_prefix()}{_sep()}{c(BOLD, label)}: "
            f"{c(BOLD, f'{val:.2f} {unit}')}",
            flush=True,
        )

    @staticmethod
    def metrics(msg: str) -> None:
        """Imprime con timestamp y texto libre (sin ': X ms')."""
        print(f"{_ts_prefix()}{_sep()}{msg}", flush=True)

    @staticmethod
    def header(title: str) -> None:
        line = "═" * 62
        print(c(CYAN, line), flush=True)
        print(c(CYAN + BOLD, f"  {title}"), flush=True)
        print(c(CYAN, line), flush=True)

    @staticmethod
    def divider() -> None:
        print(c(GRAY, "─" * 62), flush=True)
