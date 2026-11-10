from __future__ import annotations

import evdev
import pytest

from core.input_actions import InputActions
from hal.keyboard_input import KEY_PRESSED, KEY_RELEASED, KEY_REPEATED, KeyboardInput
from tests.fakes import DummyKeyboard, collect_expected


class FakeCapabilityDevice:
    def __init__(self, capabilities):
        self._capabilities = capabilities

    def capabilities(self):
        return self._capabilities


def key_event(code, value):
    return evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, code, value)


# --- supports ----------------------------------------------------------------

def test_supports_returns_true_for_a_keyboard():
    capabilities = {evdev.ecodes.EV_KEY: list(KeyboardInput.keys_mapping) + [evdev.ecodes.KEY_A, evdev.ecodes.KEY_B]}

    assert KeyboardInput.supports(FakeCapabilityDevice(capabilities)) is True


def test_supports_returns_false_for_a_mouse():
    capabilities = {
        evdev.ecodes.EV_KEY: [evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT],
        evdev.ecodes.EV_REL: [evdev.ecodes.REL_X, evdev.ecodes.REL_Y],
    }

    assert KeyboardInput.supports(FakeCapabilityDevice(capabilities)) is False


def test_supports_returns_false_without_ev_key():
    assert KeyboardInput.supports(FakeCapabilityDevice({})) is False


def test_supports_returns_false_when_a_required_key_is_missing():
    capabilities = {evdev.ecodes.EV_KEY: list(KeyboardInput.keys_mapping)[1:]}

    assert KeyboardInput.supports(FakeCapabilityDevice(capabilities)) is False


# --- a real key goes through the shared machinery -----------------------------

def test_a_key_press_reaches_emit_as_an_action():
    device = DummyKeyboard([key_event(evdev.ecodes.KEY_UP, KEY_PRESSED)])
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert events[0].action == InputActions.UP


# --- translate_event_to_action ------------------------------------------------

@pytest.mark.parametrize(
    ("code", "expected_action"),
    [
        (evdev.ecodes.KEY_UP, InputActions.UP),
        (evdev.ecodes.KEY_DOWN, InputActions.DOWN),
        (evdev.ecodes.KEY_LEFT, InputActions.LEFT),
        (evdev.ecodes.KEY_RIGHT, InputActions.RIGHT),
        (evdev.ecodes.KEY_ENTER, InputActions.SELECT),
        (evdev.ecodes.KEY_BACKSPACE, InputActions.BACK),
        (evdev.ecodes.KEY_ESC, InputActions.BACK),
    ],
)
def test_translate_event_to_action_maps_every_key(code, expected_action):
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(key_event(code, KEY_PRESSED)) == expected_action


@pytest.mark.parametrize(
    ("code", "expected_action"),
    [
        (evdev.ecodes.KEY_UP, InputActions.UP),
        (evdev.ecodes.KEY_DOWN, InputActions.DOWN),
        (evdev.ecodes.KEY_LEFT, InputActions.LEFT),
        (evdev.ecodes.KEY_RIGHT, InputActions.RIGHT),
    ],
)
def test_translate_event_to_action_repeats_movement_keys(code, expected_action):
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(key_event(code, KEY_REPEATED)) == expected_action


@pytest.mark.parametrize(
    "code",
    [evdev.ecodes.KEY_ENTER, evdev.ecodes.KEY_BACKSPACE, evdev.ecodes.KEY_ESC],
)
def test_translate_event_to_action_does_not_repeat_select_and_back(code):
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(key_event(code, KEY_REPEATED)) is None


def test_translate_event_to_action_return_none_if_key_released():
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(key_event(evdev.ecodes.KEY_UP, KEY_RELEASED)) is None


def test_translate_event_to_action_return_none_with_unknown_keys():
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(key_event(evdev.ecodes.KEY_UNKNOWN, KEY_PRESSED)) is None


def test_translate_event_to_action_return_none_with_incorrect_event_type():
    event = evdev.InputEvent(0, 0, evdev.ecodes.EV_REL, evdev.ecodes.KEY_UP, KEY_PRESSED)
    keyboard = KeyboardInput(DummyKeyboard([]))

    assert keyboard.translate_event_to_action(event) is None