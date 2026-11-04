import threading
import time

from core.input_actions import InputActions
from core.input_event import InputEvent
from hal.dummy_input import DummyInput


def collect(expected):
    """Return (emit, events, done): emit stores events, done is set after `expected` of them."""
    events = []
    done = threading.Event()

    def emit(event):
        events.append(event)
        if len(events) >= expected:
            done.set()

    return emit, events, done


# --- start -----------------------------------------------------------------

def test_start_emits_every_action_in_order():
    actions = [InputActions.DOWN, InputActions.SELECT, InputActions.UP]
    emit, events, done = collect(len(actions))
    device = DummyInput(actions, delay=0)

    device.start(emit)
    assert done.wait(timeout=2)
    device.stop()

    assert [event.action for event in events] == actions


def test_start_emits_input_events_with_the_device_name_as_source():
    emit, events, done = collect(1)
    device = DummyInput([InputActions.SELECT], delay=0)

    device.start(emit)
    assert done.wait(timeout=2)
    device.stop()

    assert isinstance(events[0], InputEvent)
    assert events[0].source == "Dummy"


def test_start_does_not_block_the_caller():
    emit, _, _ = collect(1)
    device = DummyInput([InputActions.DOWN, InputActions.DOWN], delay=5)

    started = time.perf_counter()
    device.start(emit)
    elapsed = time.perf_counter() - started
    device.stop()

    assert elapsed < 1


def test_start_with_no_actions_emits_nothing():
    emit, events, _ = collect(1)
    device = DummyInput([], delay=0)

    device.start(emit)
    device.stop()

    assert events == []


# --- stop ------------------------------------------------------------------

def test_stop_early_prevents_the_remaining_actions():
    actions = [InputActions.DOWN, InputActions.DOWN, InputActions.DOWN]
    emit, events, done = collect(1)
    device = DummyInput(actions, delay=5)

    device.start(emit)
    assert done.wait(timeout=2)   # first action emitted, now waiting 5 s
    started = time.perf_counter()
    device.stop()
    elapsed = time.perf_counter() - started

    assert len(events) == 1
    assert elapsed < 1            # stop interrupts the wait


def test_stop_can_be_called_twice():
    device = DummyInput([InputActions.DOWN], delay=0)
    device.start(lambda event: None)

    device.stop()
    device.stop()


def test_stop_before_start_does_not_fail():
    device = DummyInput([InputActions.DOWN], delay=0)

    device.stop()
