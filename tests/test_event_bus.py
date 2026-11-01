import logging
import threading
import time

from core.event_bus import EventBus
from core.events import Events


# --- subscribe -------------------------------------------------------------

def test_subscribe_to_new_event_type_registers_the_callback():
    bus = EventBus()
    received = []

    bus.subscribe(Events.INPUT_ACTION, received.append)
    bus.publish(Events.INPUT_ACTION, "x")

    assert received == ["x"]


def test_subscribe_to_existing_event_type_keeps_previous_callbacks():
    bus = EventBus()
    first, second = [], []

    bus.subscribe(Events.INPUT_ACTION, first.append)
    bus.subscribe(Events.INPUT_ACTION, second.append)
    bus.publish(Events.INPUT_ACTION, "x")

    assert first == ["x"]
    assert second == ["x"]


def test_subscribe_same_callback_twice_registers_it_once():
    bus = EventBus()
    received = []

    bus.subscribe(Events.INPUT_ACTION, received.append)
    bus.subscribe(Events.INPUT_ACTION, received.append)
    bus.publish(Events.INPUT_ACTION, "x")

    assert received == ["x"]


def test_subscriber_does_not_receive_other_event_types():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)

    bus.publish(Events.STATE_CHANGED, "other")

    assert received == []


# --- post ------------------------------------------------------------------

def test_post_does_not_deliver_before_dispatch():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)

    bus.post(Events.INPUT_ACTION, "queued")

    assert received == []


# --- dispatch_next_event ---------------------------------------------------

def test_dispatch_delivers_the_posted_event():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)
    bus.post(Events.INPUT_ACTION, "queued")

    bus.dispatch_next_event(timeout=0.01)

    assert received == ["queued"]


def test_dispatch_returns_true_when_it_delivered():
    bus = EventBus()
    bus.post(Events.INPUT_ACTION, "x")

    assert bus.dispatch_next_event(timeout=0.01) is True


def test_dispatch_returns_false_on_empty_queue():
    bus = EventBus()

    assert bus.dispatch_next_event(timeout=0.01) is False


def test_dispatch_delivers_only_one_event_per_call():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)
    bus.post(Events.INPUT_ACTION, 1)
    bus.post(Events.INPUT_ACTION, 2)

    bus.dispatch_next_event(timeout=0.01)

    assert received == [1]


def test_dispatch_keeps_arrival_order():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)

    for n in (1, 2, 3):
        bus.post(Events.INPUT_ACTION, n)
    for _ in range(3):
        bus.dispatch_next_event(timeout=0.01)

    assert received == [1, 2, 3]


def test_dispatch_waits_for_the_timeout_on_empty_queue():
    bus = EventBus()

    start = time.perf_counter()
    bus.dispatch_next_event(timeout=0.05)
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.04


# --- publish ---------------------------------------------------------------

def test_publish_delivers_data_to_subscriber():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)

    bus.publish(Events.INPUT_ACTION, "hello")

    assert received == ["hello"]


def test_publish_without_subscribers_does_not_fail():
    bus = EventBus()

    bus.publish(Events.INPUT_ACTION, "nobody listens")


def test_publish_calls_every_subscriber():
    bus = EventBus()
    first, second, third = [], [], []
    bus.subscribe(Events.INPUT_ACTION, first.append)
    bus.subscribe(Events.INPUT_ACTION, second.append)
    bus.subscribe(Events.INPUT_ACTION, third.append)

    bus.publish(Events.INPUT_ACTION, 1)

    assert first == [1]
    assert second == [1]
    assert third == [1]


def test_publish_logs_error_when_a_subscriber_fails(caplog):
    bus = EventBus()

    def broken(data):
        raise RuntimeError("boom")

    bus.subscribe(Events.INPUT_ACTION, broken)

    with caplog.at_level(logging.ERROR):
        bus.publish(Events.INPUT_ACTION, "x")

    assert "Error in subscriber" in caplog.text
    assert "boom" in caplog.text


def test_failing_subscriber_does_not_block_the_following_ones():
    bus = EventBus()
    received = []

    def broken(data):
        raise RuntimeError("boom")

    bus.subscribe(Events.INPUT_ACTION, broken)
    bus.subscribe(Events.INPUT_ACTION, received.append)

    bus.publish(Events.INPUT_ACTION, "x")

    assert received == ["x"]


# --- threads ---------------------------------------------------------------

def test_events_posted_from_another_thread_are_delivered():
    bus = EventBus()
    received = []
    bus.subscribe(Events.INPUT_ACTION, received.append)

    def producer():
        for n in (1, 2, 3):
            bus.post(Events.INPUT_ACTION, n)

    thread = threading.Thread(target=producer)
    thread.start()

    attempts = 0
    while len(received) < 3 and attempts < 50:
        bus.dispatch_next_event(timeout=0.05)
        attempts += 1
    thread.join()

    assert received == [1, 2, 3]