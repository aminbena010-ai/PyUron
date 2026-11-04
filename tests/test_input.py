import pygame
import pytest

from pyuron.input import InputManager


def _key_event(kind, key):
    return pygame.event.Event(kind, key=key)


def _mouse_event(kind, button):
    return pygame.event.Event(kind, button=button, pos=(0, 0))


def test_action_binding_and_press():
    inp = InputManager()
    inp.bind_action("jump", pygame.K_SPACE)

    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_SPACE))

    assert inp.is_action_pressed("jump")
    assert inp.is_action_just_pressed("jump")
    assert not inp.is_action_just_released("jump")

    inp.begin_frame()
    assert inp.is_action_pressed("jump")
    assert not inp.is_action_just_pressed("jump")


def test_action_release():
    inp = InputManager()
    inp.bind_action("jump", pygame.K_SPACE)

    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_SPACE))
    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYUP, pygame.K_SPACE))

    assert not inp.is_action_pressed("jump")
    assert inp.is_action_just_released("jump")


def test_multiple_keys_same_action():
    inp = InputManager()
    inp.bind_action("left", pygame.K_a, pygame.K_LEFT)

    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_LEFT))

    assert inp.is_action_pressed("left")

    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_a))
    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYUP, pygame.K_LEFT))

    assert inp.is_action_pressed("left")  # todavía A pulsada


def test_mouse_button_action():
    inp = InputManager()
    inp.bind_action("fire", pygame.BUTTON_LEFT)

    inp.begin_frame()
    inp.process_event(_mouse_event(pygame.MOUSEBUTTONDOWN, pygame.BUTTON_LEFT))

    assert inp.is_action_pressed("fire")
    assert inp.is_action_just_pressed("fire")


def test_get_vector_2d_normalized():
    inp = InputManager()
    inp.bind_action("up",    pygame.K_w)
    inp.bind_action("down",  pygame.K_s)
    inp.bind_action("left",  pygame.K_a)
    inp.bind_action("right", pygame.K_d)

    inp.begin_frame()
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_w))
    inp.process_event(_key_event(pygame.KEYDOWN, pygame.K_d))

    x, y = inp.get_vector_2d("up", "down", "left", "right")
    # Diagonal normalizada = (0.707, 0.707)
    assert x == pytest.approx(0.7071, abs=1e-3)
    assert y == pytest.approx(0.7071, abs=1e-3)


def test_unbound_action_returns_false():
    inp = InputManager()
    assert not inp.is_action_pressed("nonexistent")
    assert not inp.is_action_just_pressed("nonexistent")
