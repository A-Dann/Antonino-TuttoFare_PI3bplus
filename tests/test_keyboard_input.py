from __future__ import annotations

import evdev

from core.input_actions import InputActions
from hal.keyboard_input import KeyboardInput, KEY_PRESSED, KEY_RELEASED, KEY_REPEATED

# --- translate_event_to_action ---------------------------------------------

def test_translate_event_to_action_return_correct_action():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, KEY_PRESSED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) == InputActions.UP


def test_translate_event_to_action_return_correct_action_if_key_repeated():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, KEY_REPEATED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) == InputActions.UP


def test_translate_event_to_action_return_none_if_key_released():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UP, KEY_RELEASED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) is None


def test_translate_event_to_action_return_none_if_key_repeated_cannot_be_repeated():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, KEY_REPEATED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) is None


def test_translate_event_to_action_return_none_with_unknown_keys():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, evdev.ecodes.KEY_UNKNOWN, KEY_PRESSED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) is None


def test_translate_event_to_action_return_none_with_incorrect_event_type():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_REL, evdev.ecodes.KEY_UP, KEY_PRESSED)

    keyboard = KeyboardInput()

    assert keyboard.translate_event_to_action(event) is None