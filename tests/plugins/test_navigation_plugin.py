import pytest

from core.context import AppContext
from core.event_bus import EventBus
from core.events import Events
from core.input_actions import InputActions
from core.input_event import InputEvent
from core.state_manager import StateManager
from plugins.navigation.navigation_plugin import NavigationPlugin
from ui.navigation import Navigator
from ui.screens import Screen

OTHER_ACTIONS = [action for action in InputActions if action is not InputActions.BACK]

# --- helper functions ------------------------------------------------------


def create_context():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)
    navigation_plugin = NavigationPlugin()
    navigation_plugin.start(ctx)

    return ctx


def create_and_register_parent_child_screen(ctx: AppContext):
    parent = Screen("parent")
    child = Screen("child")

    ctx.navigator.register_screen(parent)
    ctx.navigator.register_screen(child, parent=parent.key)

    return parent, child


def press_input_action(ctx, action):
    ctx.event_bus.publish(Events.INPUT_ACTION, InputEvent(action, "test"))


# ---


def test_back_goes_to_the_parent_screen():
    ctx = create_context()
    parent, child = create_and_register_parent_child_screen(ctx)
    ctx.navigator.navigate_to(child.key)

    press_input_action(ctx, InputActions.BACK)

    assert ctx.navigator.get_active_screen() == parent


def test_back_on_a_screen_without_parent_stays_on_it():
    ctx = create_context()
    parent, _ = create_and_register_parent_child_screen(ctx)
    ctx.navigator.navigate_to(parent.key)

    press_input_action(ctx, InputActions.BACK)

    assert ctx.navigator.get_active_screen() == parent


@pytest.mark.parametrize("action", OTHER_ACTIONS)
def test_other_actions_do_not_change_the_screen(action):
    ctx = create_context()
    _, child = create_and_register_parent_child_screen(ctx)
    ctx.navigator.navigate_to(child.key)

    press_input_action(ctx, action)

    assert ctx.navigator.get_active_screen() == child
