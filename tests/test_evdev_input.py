from __future__ import annotations

import logging

import evdev
import pytest

from core.input_actions import InputActions
from hal.evdev_input import EvdevInput
from tests.fakes import FakeEvdevDevice, collect, collect_expected

# --- a minimal concrete driver ----------------------------------------------
#
# EvdevInput is abstract, so the shared behaviour (thread, select, stop...) is
# tested through the smallest possible subclass: three known codes become an
# action, any other code has no action.

ACTIONS = {
    evdev.ecodes.KEY_UP: InputActions.UP,
    evdev.ecodes.KEY_DOWN: InputActions.DOWN,
    evdev.ecodes.KEY_ENTER: InputActions.SELECT,
}


class FakeEvdevInput(EvdevInput):
    @classmethod
    def supports(cls, device):
        return True

    def translate_event_to_action(self, raw_event):
        return ACTIONS.get(raw_event.code)


class OnlySupports(EvdevInput):
    @classmethod
    def supports(cls, device):
        return True


class OnlyTranslate(EvdevInput):
    def translate_event_to_action(self, raw_event):
        return None


def raw_event(code):
    return evdev.InputEvent(0, 0, evdev.ecodes.EV_KEY, code, 1)


# --- abstract contract -------------------------------------------------------

def test_evdev_input_cannot_be_created_directly():
    with pytest.raises(TypeError, match="abstract"):
        EvdevInput(object())


@pytest.mark.parametrize("incomplete_class", [OnlySupports, OnlyTranslate])
def test_a_subclass_missing_an_abstract_method_cannot_be_created(incomplete_class):
    with pytest.raises(TypeError, match="abstract"):
        incomplete_class(object())


def test_a_subclass_with_both_abstract_methods_can_be_created():
    FakeEvdevInput(object())


# --- name --------------------------------------------------------------------

def test_name_is_the_device_name():
    driver = FakeEvdevInput(FakeEvdevDevice([]))

    assert driver.name == "fake_device"


# --- start / stop ------------------------------------------------------------

def test_start_does_not_block():
    driver = FakeEvdevInput(FakeEvdevDevice([]))

    driver.start(lambda event: None)
    driver.stop()  # reached only if start() returned


def test_stop_ends_the_thread():
    driver = FakeEvdevInput(FakeEvdevDevice([]))
    driver.start(lambda event: None)

    driver.stop()

    assert not driver._thread.is_alive()


def test_stop_closes_the_device():
    device = FakeEvdevDevice([])
    driver = FakeEvdevInput(device)
    driver.start(lambda event: None)

    driver.stop()

    assert device.is_closed


def test_stop_can_be_called_twice():
    driver = FakeEvdevInput(FakeEvdevDevice([]))
    driver.start(lambda event: None)

    driver.stop()
    driver.stop()


def test_stop_before_start_closes_the_device_without_error():
    device = FakeEvdevDevice([])
    driver = FakeEvdevInput(device)

    driver.stop()

    assert device.is_closed


# --- read_loop ---------------------------------------------------------------

def test_read_loop_emits_action_for_incoming_event():
    device = FakeEvdevDevice([raw_event(evdev.ecodes.KEY_UP)])
    emit, events, done = collect_expected(1)
    driver = FakeEvdevInput(device)

    driver.start(emit)
    device.send()
    assert done.wait(timeout=2)
    driver.stop()

    assert events[0].action == InputActions.UP


def test_read_loop_uses_the_device_name_as_source():
    device = FakeEvdevDevice([raw_event(evdev.ecodes.KEY_UP)])
    emit, events, done = collect_expected(1)
    driver = FakeEvdevInput(device)

    driver.start(emit)
    device.send()
    assert done.wait(timeout=2)
    driver.stop()

    assert events[0].source == "fake_device"


def test_read_loop_ignores_events_that_have_no_action():
    device = FakeEvdevDevice([raw_event(evdev.ecodes.KEY_A), raw_event(evdev.ecodes.KEY_DOWN)])
    emit, events, done = collect_expected(1)
    driver = FakeEvdevInput(device)

    driver.start(emit)
    device.send()
    assert done.wait(timeout=2)
    driver.stop()

    assert [event.action for event in events] == [InputActions.DOWN]


def test_read_loop_emits_several_events_in_order():
    device = FakeEvdevDevice([
        raw_event(evdev.ecodes.KEY_UP),
        raw_event(evdev.ecodes.KEY_DOWN),
        raw_event(evdev.ecodes.KEY_ENTER),
    ])
    emit, events, done = collect_expected(3)
    driver = FakeEvdevInput(device)

    driver.start(emit)
    device.send()
    assert done.wait(timeout=2)
    driver.stop()

    assert [event.action for event in events] == [InputActions.UP, InputActions.DOWN, InputActions.SELECT]


def test_read_loop_ends_when_the_device_is_unplugged(caplog):
    device = FakeEvdevDevice([], error=OSError("device unplugged"))
    emit, events, done = collect_expected(1)
    driver = FakeEvdevInput(device)

    with caplog.at_level(logging.ERROR):
        driver.start(emit)
        device.send()
        driver._thread.join(timeout=2)

    assert not driver._thread.is_alive()
    assert events == []
    assert "Something went wrong" in caplog.text
    driver.stop()


def test_unplugged_device_is_closed_only_by_stop():
    device = FakeEvdevDevice([], error=OSError("device unplugged"))
    driver = FakeEvdevInput(device)
    driver.start(lambda event: None)
    device.send()
    driver._thread.join(timeout=2)

    assert not device.is_closed

    driver.stop()

    assert device.is_closed


def test_read_loop_survives_a_read_with_no_events_available():
    device = FakeEvdevDevice([raw_event(evdev.ecodes.KEY_UP)], first_read_error=BlockingIOError())
    emit, events, done = collect_expected(1)
    driver = FakeEvdevInput(device)

    driver.start(emit)
    device.send()  # the first read raises BlockingIOError
    device.send()  # the second read delivers the event
    assert done.wait(timeout=2)
    driver.stop()

    assert events[0].action == InputActions.UP


# --- emit_action -------------------------------------------------------------

def test_emit_action_emits_action():
    emit, events = collect()
    driver = FakeEvdevInput(FakeEvdevDevice([]))

    driver.emit_action(raw_event(evdev.ecodes.KEY_UP), emit)

    assert events[0].action == InputActions.UP


def test_emit_action_does_not_emit_when_action_is_none():
    emit, events = collect()
    driver = FakeEvdevInput(FakeEvdevDevice([]))

    driver.emit_action(raw_event(evdev.ecodes.KEY_A), emit)

    assert events == []
