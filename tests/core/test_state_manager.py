import logging

from core.event_bus import EventBus
from core.events import Events
from core.state_changed import StateChanged
from core.state_keys import StateKeys
from core.state_manager import StateManager

# --- get -------------------------------------------------------------------

def test_initial_language_is_english():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    assert state_manager.get(StateKeys.LANGUAGE) == "en"


def test_initial_active_screen_is_none():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    assert state_manager.get(StateKeys.ACTIVE_SCREEN) is None


def test_initial_selected_index_is_zero():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    assert state_manager.get(StateKeys.SELECTED_INDEX) == 0


def test_initial_flags_are_correct():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    assert state_manager.get(StateKeys.AI_AGENT_RUNNING) is False
    assert state_manager.get(StateKeys.ANTENNA_CONNECTED) is False
    assert state_manager.get(StateKeys.MICROPHONE_CONNECTED) is False
    assert state_manager.get(StateKeys.SPEAKER_CONNECTED) is False
    assert state_manager.get(StateKeys.WIFI_CONNECTED) is False
    assert state_manager.get(StateKeys.RUNNING) is True


def test_get_returns_none_for_unknown_key():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    assert state_manager.get("Unknown Key") is None


# --- set -------------------------------------------------------------------

def test_set_changes_the_stored_value():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "a")
    assert state_manager.get(StateKeys.ACTIVE_SCREEN) == "a"


def test_set_publishes_state_changed_with_key_and_value():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    received = []
    event_bus.subscribe(Events.STATE_CHANGED, received.append)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "a")

    assert received == [StateChanged(StateKeys.ACTIVE_SCREEN, "a")]


def test_set_with_same_value_does_not_publish():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    received = []
    event_bus.subscribe(Events.STATE_CHANGED, received.append)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "a")
    state_manager.set(StateKeys.ACTIVE_SCREEN, "a")

    assert len(received) == 1


def test_set_with_new_value_publishes_again():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    received = []
    event_bus.subscribe(Events.STATE_CHANGED, received.append)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "a")
    state_manager.set(StateKeys.ACTIVE_SCREEN, "b")

    assert len(received) == 2


# --- unknown keys ----------------------------------------------------------

def test_get_with_unknown_key_logs_a_warning_with_the_key(caplog):
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    with caplog.at_level(logging.WARNING):
        state_manager.get("typo")

    assert "Unknown state key: typo" in caplog.text


def test_set_with_unknown_key_does_not_store_the_value():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    state_manager.set("typo", 5)

    assert state_manager.get("typo") is None


def test_set_with_unknown_key_does_not_publish():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    received = []
    event_bus.subscribe(Events.STATE_CHANGED, received.append)

    state_manager.set("typo", 5)

    assert received == []


def test_set_with_unknown_key_logs_a_warning_with_the_key(caplog):
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    with caplog.at_level(logging.WARNING):
        state_manager.set("typo", 5)

    assert "Unknown state key: typo" in caplog.text


def test_known_keys_do_not_log_a_warning(caplog):
    event_bus = EventBus()
    state_manager = StateManager(event_bus)

    with caplog.at_level(logging.WARNING):
        state_manager.set(StateKeys.SELECTED_INDEX, 3)
        state_manager.get(StateKeys.SELECTED_INDEX)

    assert "Unknown state key" not in caplog.text
