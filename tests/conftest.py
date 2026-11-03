"""Configura pytest para cronometrar cada test con el estilo PyUron."""
from __future__ import annotations

import pytest

from pyuron.core.logger import GREEN, RED, Log, c

_timings: list[tuple[str, float, str]] = []


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    ms = (report.stop - report.start) * 1000.0
    if report.passed:
        status = c(GREEN, "PASS")
    elif report.failed:
        status = c(RED, "FAIL")
    else:
        status = c(RED, "SKIP")

    short = report.nodeid.split("::")[-1]
    _timings.append((short, ms, status))
    Log.time(f"{status}  {short}", ms)


def pytest_sessionfinish(session, exitstatus):
    if not _timings:
        return
    total = sum(ms for _, ms, _ in _timings)
    avg = total / len(_timings)
    print()
    Log.header(f"Resumen: {len(_timings)} test(s)")
    Log.time("Tiempo total", total)
    Log.time("Tiempo medio por test", avg)
