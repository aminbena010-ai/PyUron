"""Banner de bienvenida de PyUron."""
from __future__ import annotations

import platform
import sys

from pyuron.core.logger import BOLD, CYAN, DIM, GRAY, MAGENTA, YELLOW, c

LOGO = r"""
    ____        _   _
   |  _ \ _   _| | | |_ __ ___  _ __
   | |_) | | | | | | | '__/ _ \| '_ \
   |  __/| |_| | |_| | | | (_) | | | |
   |_|    \__, |\___/|_|  \___/|_| |_|
          |___/
"""


def show_banner(version: str = "1.0.0") -> None:
    print(c(MAGENTA, LOGO), flush=True)
    print(
        c(CYAN, "  ◆ ") + c(BOLD, f"PyUron {version}") + c(GRAY, "  ·  Core Engine"),
        flush=True,
    )
    py = sys.version_info
    print(
        c(GRAY, f"  ◆ Python {py.major}.{py.minor}.{py.micro}  ·  "
                f"{platform.system()} {platform.release()}"),
        flush=True,
    )
    print(c(GRAY, "  ◆ ") + c(YELLOW, "ctrl+c para salir"), flush=True)
    print(c(DIM, "─" * 62), flush=True)
