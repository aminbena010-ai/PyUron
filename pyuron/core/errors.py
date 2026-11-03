"""Manejador de excepciones con diagnóstico claro para el usuario."""
from __future__ import annotations

import sys
import traceback

from pyuron.core.logger import BOLD, GRAY, Log, c


def _suggestions(exc: BaseException) -> list[str]:
    """Devuelve sugerencias concretas según el tipo de excepción."""
    tips: list[str] = []

    if isinstance(exc, ModuleNotFoundError):
        mod = getattr(exc, "name", None) or "?"
        tips.append(f"Falta el módulo '{mod}'.")
        tips.append(f"Instálalo con:  uv add {mod}")
        tips.append("O asegúrate de ejecutar con:  uv run python main.py")
    elif isinstance(exc, AttributeError):
        attr = getattr(exc, "name", None) or "?"
        tips.append(f"El objeto no tiene el atributo '{attr}'.")
        tips.append("Revisa la ortografía del nombre y que sea del tipo correcto.")
    elif isinstance(exc, NameError):
        tips.append("Hay un nombre no definido.")
        tips.append("¿Falta un import? ¿Una variable no declarada?")
    elif isinstance(exc, TypeError):
        tips.append("Tipos incorrectos en una llamada.")
        tips.append("Revisa el número y tipo de argumentos.")
    elif isinstance(exc, KeyError):
        tips.append(f"Falta la clave {exc} en el diccionario.")
        tips.append("Verifica las claves disponibles con .keys().")
    elif isinstance(exc, IndexError):
        tips.append("Índice fuera de rango. Revisa len() de la lista.")
    elif isinstance(exc, FileNotFoundError):
        tips.append(f"No existe el archivo: {getattr(exc, 'filename', '?')}")
        tips.append("Revisa la ruta relativa desde donde ejecutas.")
    elif isinstance(exc, (ValueError, AssertionError)):
        tips.append("Un valor no cumple lo esperado.")
        tips.append("Revisa el mensaje del error.")
    elif isinstance(exc, ZeroDivisionError):
        tips.append("Estás dividiendo entre cero.")
    else:
        tips.append("Revisa el mensaje y el archivo:línea mostrados arriba.")

    return tips


def install_exception_hook() -> None:
    """Reemplaza sys.excepthook por uno con diagnóstico legible."""

    def hook(exc_type, exc_value, exc_tb):
        # KeyboardInterrupt se muestra como una salida normal.
        if issubclass(exc_type, KeyboardInterrupt):
            print()
            Log.info("Interrumpido por el usuario (Ctrl+C).")
            return

        print()
        Log.header("ERROR EN PyUron")
        Log.err(f"Tipo:    {exc_type.__name__}")
        Log.err(f"Mensaje: {exc_value}")

        frames = traceback.extract_tb(exc_tb)
        if frames:
            last = frames[-1]
            print()
            Log.warn(f"Ocurrió en: {last.filename}:{last.lineno}")
            if last.line:
                print(f"    {c(GRAY, last.line.strip())}")

            print()
            print(c(GRAY, "  Pila de llamadas:"))
            for summary in traceback.format_tb(exc_tb)[-6:]:
                for line in summary.rstrip().split("\n"):
                    print(c(GRAY, f"    {line}"))

        print()
        print(c(BOLD + CYAN_, "Sugerencias:"))
        for tip in _suggestions(exc_value):
            print(f"    {c(GRAY, '→')} {tip}")

        print()
        Log.info("Si necesitas ayuda, copia este bloque completo.")
        print()
        sys.exit(1)

    sys.excepthook = hook


# Alias local para evitar import circular en tiempo de decoración.
from pyuron.core.logger import CYAN as CYAN_  # noqa: E402
