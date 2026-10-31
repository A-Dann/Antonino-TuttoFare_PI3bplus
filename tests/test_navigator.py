import logging

from core.event_bus import EventBus
from core.state_keys import StateKeys
from core.state_manager import StateManager
from ui.navigation import Navigator
from ui.screens import MenuScreen

# --- Helper Funcions ---

def make_navigator():
    state_manager = StateManager(EventBus())
    navigator = Navigator(state_manager)
    return navigator, state_manager


def make_screen(key):
    return MenuScreen(key=key, title=key, options=[])


# --- register_screen -------------------------------------------------------

def test_register_screen_makes_screen_available_when_active():
    navigator, state_manager = make_navigator()
    screen_a = make_screen("A")
    navigator.register_screen(screen_a)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


def test_register_screen_twice_keeps_the_first_screen():
    navigator, state_manager = make_navigator()
    first = make_screen("A")
    second = make_screen("A")

    navigator.register_screen(first)
    navigator.register_screen(second)

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is first


def test_register_screen_twice_ignores_the_new_actions():
    navigator, state_manager = make_navigator()
    first_calls = []
    second_calls = []
    navigator.register_screen(make_screen("A"), {"go": first_calls.append})
    navigator.register_screen(make_screen("A"), {"go": second_calls.append})

    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")

    assert len(first_calls) == 1
    assert second_calls == []

    
def test_register_screen_twice_logs_warning(caplog):
    navigator, _ = make_navigator()

    navigator.register_screen(make_screen("A"))

    with caplog.at_level(logging.WARNING):
        navigator.register_screen(make_screen("A"))

    assert "already registered" in caplog.text


def test_register_screen_without_actions_is_allowed():
    navigator, state_manager = make_navigator()
    screen_a = make_screen("A")

    navigator.register_screen(screen_a)
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


# --- get_active_screen -----------------------------------------------------

def test_get_active_screen_returns_the_screen_matching_active_key():
    navigator, state_manager = make_navigator()
    screen_a = make_screen("A")

    navigator.register_screen(screen_a)
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    assert navigator.get_active_screen() is screen_a


def test_get_active_screen_returns_none_when_no_screen_is_active():
    navigator, _ = make_navigator()
    navigator.register_screen(make_screen("A"))

    assert navigator.get_active_screen() is None


def test_get_active_screen_returns_none_for_unregistered_key():
    navigator, state_manager = make_navigator()
    navigator.register_screen(make_screen("A"))

    state_manager.set(StateKeys.ACTIVE_SCREEN, "B")

    assert navigator.get_active_screen() is None


# --- execute_action --------------------------------------------------------

def test_execute_action_runs_the_registered_action():
    navigator, state_manager = make_navigator()
    calls = []
    navigator.register_screen(make_screen("A"), {"go": calls.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")

    assert len(calls) == 1


def test_execute_action_passes_ctx_to_the_action():
    navigator, state_manager = make_navigator()
    calls = []
    ctx = object()
    navigator.register_screen(make_screen("A"), {"go": calls.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(ctx, "go")

    assert calls == [ctx]


def test_execute_action_does_not_run_actions_of_other_screens():
    navigator, state_manager = make_navigator()
    calls_a = []
    calls_b = []
    navigator.register_screen(make_screen("A"), {"go": calls_a.append})
    navigator.register_screen(make_screen("B"), {"go": calls_b.append})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    navigator.execute_action(object(), "go")
    assert len(calls_a) == 1
    assert calls_b == []


def test_execute_action_logs_warning_for_unknown_action(caplog):
    navigator, state_manager = make_navigator()
    navigator.register_screen(make_screen("A"), {"go": lambda ctx: None})
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "does not exist")

    assert "No action found" in caplog.text


def test_execute_action_logs_warning_when_screen_has_no_actions(caplog):
    navigator, state_manager = make_navigator()
    navigator.register_screen(make_screen("A"))
    state_manager.set(StateKeys.ACTIVE_SCREEN, "A")

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "go")

    assert "No action found" in caplog.text


def test_execute_action_logs_warning_when_no_screen_is_active(caplog):
    navigator, _ = make_navigator()

    with caplog.at_level(logging.WARNING):
        navigator.execute_action(object(), "does not exist")

    assert "No action found" in caplog.text


# --- isolation -------------------------------------------------------------

def test_two_navigators_do_not_share_registered_screens():
    first_navigator, first_state = make_navigator()
    second_navigator, second_state = make_navigator()
    first_navigator.register_screen(make_screen("A"))

    first_state.set(StateKeys.ACTIVE_SCREEN, "A")
    second_state.set(StateKeys.ACTIVE_SCREEN, "A")

    assert first_navigator.get_active_screen() is not None
    assert second_navigator.get_active_screen() is None