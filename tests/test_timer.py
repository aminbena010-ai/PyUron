import pytest

from pyuron.core.timer import Cooldown, Stopwatch


def test_cooldown_triggers_once():
    cd = Cooldown(0.2)
    assert cd.trigger() is True
    assert cd.trigger() is False
    cd.update(0.1)
    assert cd.trigger() is False
    cd.update(0.15)
    assert cd.trigger() is True


def test_cooldown_progress():
    cd = Cooldown(1.0)
    cd.trigger()
    assert cd.progress == pytest.approx(0.0)
    cd.update(0.5)
    assert cd.progress == pytest.approx(0.5)
    cd.update(0.5)
    assert cd.progress == pytest.approx(1.0)


def test_cooldown_rejects_negative():
    with pytest.raises(ValueError):
        Cooldown(-1)


def test_stopwatch_accumulates():
    sw = Stopwatch()
    sw.update(0.1)
    sw.update(0.2)
    assert sw.elapsed == pytest.approx(0.3)
    sw.reset()
    assert sw.elapsed == pytest.approx(0.0)
