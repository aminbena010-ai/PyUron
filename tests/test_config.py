import pytest

from pyuron import EngineConfig


def test_default_config_has_valid_dimensions():
    c = EngineConfig()
    assert c.width > 0 and c.height > 0


def test_rejects_invalid_dimensions():
    with pytest.raises(ValueError):
        EngineConfig(width=0)


def test_rejects_invalid_clear_color():
    with pytest.raises(ValueError):
        EngineConfig(clear_color=(1.0, 0.0, 0.0))
