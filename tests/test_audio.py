import pytest

from pyuron.audio.audio_manager import AudioManager


def test_volume_clamping():
    audio = AudioManager()
    audio.set_master_volume(1.5)
    assert audio.master_volume == 1.0
    audio.set_master_volume(-0.5)
    assert audio.master_volume == 0.0
    audio.set_master_volume(0.5)
    assert audio.master_volume == pytest.approx(0.5)


def test_does_not_crash_without_init():
    """Sin init, las llamadas de reproducción deben devolver None sin romper."""
    audio = AudioManager()
    # No llamamos a init() — así evitamos depender de una tarjeta de sonido
    audio.set_master_volume(0.3)
    audio.stop_music()
    audio.pause_music()
    audio.resume_music()
    assert audio.master_volume == pytest.approx(0.3)
