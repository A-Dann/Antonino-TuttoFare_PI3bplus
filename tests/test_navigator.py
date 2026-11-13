import logging

from core.event_bus import EventBus
from core.events import Events
from core.state_keys import StateKeys
from core.state_manager import StateManager
from ui.navigation import Navigator
from ui.screens import Screen

# --- Helper Funcions ---

def make_navigator():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    return navigator, state_manager, event_bus


def make_screen(key):
    return Screen(key=key)


# --- register_screen -------------------------------------------------------

def test_register_screen_makes_screen_available_when_active():
    navigator, state_manager, _= make_navigator()
    screen_a = make_screen("A")
    navigator.register_screen(screen_a)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


def test_register_screen_twice_keeps_the_first_screen():
    navigator, state_manager, _ = make_navigator()
    first = make_screen("A")
    second = make_screen("A")

    navigator.register_screen(first)
    navigator.register_screen(second)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is first


def test_register_screen_twice_ignores_the_new_actions():
    navigator, state_manager, _ = make_navigator()
    first_calls = []
    second_calls = []
    navigator.register_screen(make_screen("A"), {"go": first_calls.append})
    navigator.register_screen(make_screen("A"), {"go": second_calls.append})

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")

    assert len(first_calls) == 1
    assert second_calls == []


def test_register_screen_twice_logs_warning(caplog):
    navigator, _, _ = make_navigator()

    navigator.register_screen(make_screen("A"))

    with caplog.at_level(logging.WARNING):
        navigator.register_screen(make_screen("A"))

    assert "already registered" in caplog.text


def test_register_screen_without_actions_is_allowed():
    navigator, state_manager, _ = make_navigator()
    screen_a = make_screen("A")

    navigator.register_screen(screen_a)
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


# --- get_active_screen -----------------------------------------------------

def test_get_active_screen_returns_the_screen_matching_active_key():
    navigator, state_manager, _ = make_navigator()
    screen_a = make_screen("A")

    navigator.register_screen(screen_a)
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


def test_get_active_screen_returns_none_when_no_screen_is_active():
    navigator, _, _ = make_navigator()
    navigator.register_screen(make_screen("A"))

    assert navigator.get_active_screen() is None


def test_get_active_screen_returns_none_for_unregistered_key():
    navigator, state_manager, _ = make_navigator()
    navigator.register_screen(make_screen("A"))

    state_manager.set(StateKeys.ACTIVE_SCREEN, "B")

    assert navigator.get_active_screen() is None


# --- navigate_to ----------------------------------------------------------

def test_navigate_to_sets_active_screen_and_resets_selected_index():
    navigator, state_manager, _ = make_navigator()
    navigator.register_screen(make_screen("A"))

    state_manager.set(StateKeys.SELECTED_INDEX, 5)  # Set to a non-zero value
    navigator.navigate_to("A")

    assert state_manager.get(StateKeys.ACTIVE_SCREEN) == "A"
    assert state_manager.get(StateKeys.SELECTED_INDEX) == 0  # Should be reset to 0


def test_navigate_to_logs_warning_for_unregistered_screen(caplog):
    navigator, state_manager, _ = make_navigator()

    with caplog.at_level(logging.WARNING):
        navigator.navigate_to("NonExistentScreen")

    assert "Attempted to navigate to unregistered screen" in caplog.text
    assert state_manager.get(StateKeys.ACTIVE_SCREEN) is None  # Active screen should remain unchanged
    assert state_manager.get(StateKeys.SELECTED_INDEX) == 0  # Selected index should remain unchanged


def test_navigate_to_logs_debug_for_same_screen(caplog):
    navigator, state_manager, event_bus = make_navigator()
    navigator.register_screen(make_screen("A"))
    navigator.navigate_to("A")
    state_manager.set(StateKeys.SELECTED_INDEX, 2)  # Change selected index
    received_events = []
    event_bus.subscribe(Events.STATE_CHANGED, lambda event: received_events.append(event))

    with caplog.at_level(logging.DEBUG):
        navigator.navigate_to("A")  # Second navigation, should log debug

    assert "Already on screen" in caplog.text
    assert state_manager.get(StateKeys.ACTIVE_SCREEN) == "A"  # Active screen should remain unchanged
    assert state_manager.get(StateKeys.SELECTED_INDEX) == 2  # Selected index should remain unchanged
    assert received_events == []  # No state change events should be published


def test_navigate_subscriber_does_not_see_incoherent_state():
    navigator, state_manager, event_bus = make_navigator()
    navigator.register_screen(make_screen("A"))
    navigator.navigate_to("A")
    state_manager.set(StateKeys.SELECTED_INDEX, 2)

    snapshots = []
    def _screen_state_snapshot(event):
        active_screen_key = state_manager.get(StateKeys.ACTIVE_SCREEN)
        active_screen_index = state_manager.get(StateKeys.SELECTED_INDEX)
        snapshots.append((active_screen_key, active_screen_index))

    event_bus.subscribe(Events.STATE_CHANGED, _screen_state_snapshot)
    navigator.register_screen(make_screen("B"))
    navigator.navigate_to("B")

    assert snapshots
    assert ("B", 2) not in snapshots


# --- execute_action --------------------------------------------------------

def test_execute_action_runs_the_registered_action():
    navigator, state_manager, _ = make_navigator()
    calls = []
    navigator.register_screen(make_screen("A"), {"go": calls.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")

    assert len(calls) == 1


def test_execute_action_passes_ctx_to_the_action():
    navigator, state_manager, _ = make_navigator()
    calls = []
    ctx = object()
    navigator.register_screen(make_screen("A"), {"go": calls.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(ctx, "go")

    assert calls == [ctx]


def test_execute_action_does_not_run_actions_of_other_screens():
    navigator, state_manager, _ = make_navigator()
    calls_a = []
    calls_b = []
    navigator.register_screen(make_screen("A"), {"go": calls_a.append})
    navigator.register_screen(make_screen("B"), {"go": calls_b.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")
    assert len(calls_a) == 1
    assert calls_b == []


def test_execute_action_logs_warning_for_unknown_action(caplog):
    navigator, state_manager, _ = make_navigator()
    navigator.register_screen(make_screen("A"), {"go": lambda ctx: None})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "does not exist")

    assert "No action found" in caplog.text


def test_execute_action_logs_warning_when_screen_has_no_actions(caplog):
    navigator, state_manager, _ = make_navigator()
    navigator.register_screen(make_screen("A"))
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "go")

    assert "No action found" in caplog.text


def test_execute_action_logs_warning_when_no_screen_is_active(caplog):
    navigator, _, _ = make_navigator()

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "does not exist")

    assert "No action found" in caplog.text


# --- isolation -------------------------------------------------------------

def test_two_navigators_do_not_share_registered_screens():
    first_navigator, first_state, _ = make_navigator()
    second_navigator, second_state, _ = make_navigator()
    first_navigator.register_screen(make_screen("A"))

    first_state.set(StateKeys.ACTIVE_SCREEN, "A")
    second_state.set(StateKeys.ACTIVE_SCREEN, "A")

    assert first_navigator.get_active_screen() is not None
    assert second_navigator.get_active_screen() is None
