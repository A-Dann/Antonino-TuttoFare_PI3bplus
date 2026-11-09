from __future__ import annotations

import logging
import os
import threading

import evdev
import pytest

from core.input_actions import InputActions
from hal.keyboard_input import KEY_PRESSED, KEY_RELEASED, KEY_REPEATED, KeyboardInput

# --- helper functions ------------------------------------------------------


class DummyKeyboard:
    """Fake evdev device: a pipe plays the role of /dev/input/eventN.

    send() writes a byte into the pipe, which makes select() report the
    device as ready, exactly as a real key press would.
    """

    name = "dummy_keyboard"

    def __init__(self, events, error=None, first_read_error = None):
        self._read_fd, self._write_fd = os.pipe()
        self.fd = self._read_fd
        self._events = events
        self._error = error
        self._first_read_error = first_read_error
        self.is_closed = False

    def send(self):
        os.write(self._write_fd, b"x")

    def read(self):
        os.read(self._read_fd, 1)  # consume the byte, otherwise select() stays "ready"
        if self._first_read_error is not None:
            error, self._first_read_error = self._first_read_error, None
            raise error
        if self._error is not None:
            raise self._error
        yield from self._events

    def close(self):
        if not self.is_closed:
            os.close(self._read_fd)
            os.close(self._write_fd)
        self.is_closed = True

class FakeCapabilityDevice:
    def __init__(self, capabilities):
        self._capabilities = capabilities

    def capabilities(self):
        return self._capabilities

def key_event(code, value):
    return evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, code, value)


def collect():
    """Return (emit, events): emit stores every event it receives."""
    events = []

    def emit(event):
        events.append(event)

    return emit, events


def collect_expected(expected):
    """Like collect(), but also return `done`, set when `expected` events have arrived.

    Needed when emit is called from another thread: the test waits on `done`
    instead of guessing how long to sleep.
    """
    events = []
    done = threading.Event()

    def emit(event):
        events.append(event)
        if len(events) >= expected:
            done.set()

    return emit, events, done


# --- start / stop ----------------------------------------------------------

def test_start_does_not_block():
    keyboard = KeyboardInput(DummyKeyboard([]))

    keyboard.start(lambda event: None)
    keyboard.stop()  # reached only if start() returned


def test_stop_ends_the_thread():
    keyboard = KeyboardInput(DummyKeyboard([]))
    keyboard.start(lambda event: None)

    keyboard.stop()

    assert not keyboard._thread.is_alive()


def test_stop_closes_the_device():
    device = DummyKeyboard([])
    keyboard = KeyboardInput(device)
    keyboard.start(lambda event: None)

    keyboard.stop()

    assert device.is_closed


def test_stop_can_be_called_twice():
    keyboard = KeyboardInput(DummyKeyboard([]))
    keyboard.start(lambda event: None)

    keyboard.stop()
    keyboard.stop()


def test_stop_before_start_closes_the_device_without_error():
    device = DummyKeyboard([])
    keyboard = KeyboardInput(device)

    keyboard.stop()

    assert device.is_closed

# --- supports --------------------------------------------------------------

def test_supports_returns_true_for_a_keyboard():
    keyboard_capabilities = {
        evdev.ecodes.EV_KEY: list(KeyboardInput.keys_mapping) + [evdev.ecodes.KEY_A, evdev.ecodes.KEY_B]
    }
    keyboard = FakeCapabilityDevice(keyboard_capabilities)

    assert KeyboardInput.supports(keyboard) is True


def test_supports_returns_false_for_a_mouse():
    mouse_capabilities = {
        evdev.ecodes.EV_KEY: [
            evdev.ecodes.BTN_LEFT,
            evdev.ecodes.BTN_RIGHT,
        ],
        evdev.ecodes.EV_REL: [
            evdev.ecodes.REL_X,
            evdev.ecodes.REL_Y,
        ]
    }
    mouse = FakeCapabilityDevice(mouse_capabilities)

    assert KeyboardInput.supports(mouse) is False


def test_supports_returns_false_without_ev_key():
    no_capabilities = {}
    device_with_no_capabilities = FakeCapabilityDevice(no_capabilities)

    assert KeyboardInput.supports(device_with_no_capabilities) is False


def test_supports_returns_false_when_a_required_key_is_missing():
    keyboard_missing_capabilities = {
        evdev.ecodes.EV_KEY: list(KeyboardInput.keys_mapping)[1:] + [evdev.ecodes.KEY_A, evdev.ecodes.KEY_B]
    }
    almost_a_keyboard = FakeCapabilityDevice(keyboard_missing_capabilities)

    assert KeyboardInput.supports(almost_a_keyboard) is False


# --- read_loop -------------------------------------------------------------

def test_read_loop_emits_action_for_incoming_event():
    device = DummyKeyboard([key_event(evdev.ecodes.KEY_UP, KEY_PRESSED)])
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert events[0].action == InputActions.UP


def test_read_loop_uses_the_device_name_as_source():
    device = DummyKeyboard([key_event(evdev.ecodes.KEY_UP, KEY_PRESSED)])
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert events[0].source == "dummy_keyboard"


def test_read_loop_ignores_events_that_have_no_action():
    device = DummyKeyboard([
        key_event(evdev.ecodes.KEY_UP, KEY_RELEASED),
        key_event(evdev.ecodes.KEY_DOWN, KEY_PRESSED),
    ])
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert [event.action for event in events] == [InputActions.DOWN]

def test_read_loop_ignores_events_that_are_not_keys():
    device = DummyKeyboard([
        evdev.InputEvent(0, 0, evdev.ecodes.EV_REL, evdev.ecodes.KEY_UP, KEY_PRESSED),
        key_event(evdev.ecodes.KEY_DOWN, KEY_PRESSED),
    ])
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert [event.action for event in events] == [InputActions.DOWN]

def test_read_loop_emits_several_events_in_order():
    device = DummyKeyboard([
        key_event(evdev.ecodes.KEY_UP, KEY_PRESSED),
        key_event(evdev.ecodes.KEY_DOWN, KEY_PRESSED),
        key_event(evdev.ecodes.KEY_ENTER, KEY_PRESSED),
    ])
    emit, events, done = collect_expected(3)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()
    assert done.wait(timeout=2)
    keyboard.stop()

    assert [event.action for event in events] == [InputActions.UP, InputActions.DOWN, InputActions.SELECT]


def test_read_loop_ends_when_the_device_is_unplugged(caplog):
    device = DummyKeyboard([], error=OSError("device unplugged"))
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    with caplog.at_level(logging.ERROR):
        keyboard.start(emit)
        device.send()
        keyboard._thread.join(timeout=2)

    assert not keyboard._thread.is_alive()
    assert events == []
    assert "Something went wrong" in caplog.text
    keyboard.stop()


def test_unplugged_device_is_closed_only_by_stop():
    device = DummyKeyboard([], error=OSError("device unplugged"))
    keyboard = KeyboardInput(device)
    keyboard.start(lambda event: None)
    device.send()
    keyboard._thread.join(timeout=2)

    assert not device.is_closed

    keyboard.stop()

    assert device.is_closed


def test_read_loop_survives_a_read_with_no_events_available():
    device = DummyKeyboard(
        [key_event(evdev.ecodes.KEY_UP, KEY_PRESSED)],
        first_read_error=BlockingIOError(),
    )
    emit, events, done = collect_expected(1)
    keyboard = KeyboardInput(device)

    keyboard.start(emit)
    device.send()  # the first read raises BlockingIOError
    device.send()  # the second read delivers the event
    assert done.wait(timeout=2)
    keyboard.stop()

    assert events[0].action == InputActions.UP


# --- emit_action -----------------------------------------------------------

def test_emit_action_emits_action():
    emit, events = collect()
    event = key_event(evdev.ecodes.KEY_UP, KEY_PRESSED)
    keyboard = KeyboardInput(DummyKeyboard([]))

    keyboard.emit_action(event, emit)

    assert events[0].action == InputActions.UP


def test_emit_action_does_not_emit_when_action_is_none():
    emit, events = collect()
    event = key_event(evdev.ecodes.KEY_UNKNOWN, KEY_PRESSED)  # unknown key: no action
    keyboard = KeyboardInput(DummyKeyboard([]))

    keyboard.emit_action(event, emit)

    assert len(events) == 0


# --- translate_event_to_action ---------------------------------------------

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
