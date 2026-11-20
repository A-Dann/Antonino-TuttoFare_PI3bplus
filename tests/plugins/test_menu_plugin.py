from core.context import AppContext
from core.event_bus import EventBus
from core.events import Events
from core.input_actions import InputActions
from core.input_event import InputEvent
from core.state_keys import StateKeys
from core.state_manager import StateManager
from plugins.menu.main_menu import main_screen
from plugins.menu.menu_plugin import MenuPlugin
from plugins.menu.settings_menu import settings_screen
from plugins.navigation.navigation_plugin import NavigationPlugin
from ui.navigation import Navigator
from ui.screens import MenuItem, MenuScreen, Screen

# --- Helper functions ---

def create_context():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)
    menu_plugin = MenuPlugin()
    menu_plugin.start(ctx)

    test_menu = MenuScreen(
        key="Test",
        title="Test Menu",
        options=(
            MenuItem("a", "Option A"),
            MenuItem("b", "Option B"),
            MenuItem("c", "Option C")
        )
    )

    calls = []

    navigator.register_screen(test_menu, {
        "a": lambda ctx: calls.append("a"),
        "b": lambda ctx: calls.append("b"),
        "c": lambda ctx: calls.append("c"),
    })
    navigator.navigate_to(test_menu.key)

    return ctx, calls

def create_main_menu_context():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)
    MenuPlugin().start(ctx)
    NavigationPlugin().start(ctx)
    navigator.navigate_to(main_screen.key)

    return ctx

def press_input_action(ctx, action):
    input_event = InputEvent(action, "test")
    ctx.event_bus.publish(Events.INPUT_ACTION, input_event)

# ---

def test_down_then_select_runs_the_second_option_action():
    ctx, calls = create_context()

    # Move down to the second option
    press_input_action(ctx, InputActions.DOWN)
    # Select the second option
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen().key == "Test"
    assert calls == ["b"]


def test_select_without_moving_runs_the_first_option_action():
    ctx, calls = create_context()

    # Select the first option
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen().key == "Test"
    assert calls == ["a"]


def test_up_from_first_option_wraps_to_the_last():
    ctx, calls = create_context()

    # Move up from the first option
    press_input_action(ctx, InputActions.UP)
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen().key == "Test"
    assert calls == ["c"]


def test_down_from_last_option_wraps_to_the_first():
    ctx, calls = create_context()

    press_input_action(ctx, InputActions.UP)  # Move to last option
    press_input_action(ctx, InputActions.DOWN) # Move down from the last option
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen().key == "Test"
    assert calls == ["a"]


def test_move_updates_selected_index_in_state_manager():
    ctx, _ = create_context()

    # Move down to the second option
    press_input_action(ctx, InputActions.DOWN)

    assert ctx.state_manager.get(StateKeys.SELECTED_INDEX) == 1


def test_input_is_ignored_when_active_screen_is_not_a_menu():
    ctx, _ = create_context()

    class NonMenuScreen(Screen):
        pass

    non_menu_calls = []

    ctx.navigator.register_screen(NonMenuScreen(key="NonMenu"), {"x": lambda ctx: non_menu_calls.append("x")})
    ctx.navigator.navigate_to("NonMenu")

    # Publish an input action while on a non-menu screen
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen().key == "NonMenu"
    assert non_menu_calls == []  # No action should have been called


def test_input_on_menu_without_options_does_nothing(caplog):
    ctx, _ = create_context()

    # Create a menu screen with no options
    empty_menu = MenuScreen(key="Empty", title="Empty Menu", options=())
    ctx.navigator.register_screen(empty_menu, {})
    ctx.navigator.navigate_to(empty_menu.key)

    # Publish an input action while on a menu with no options
    press_input_action(ctx, InputActions.UP)
    press_input_action(ctx, InputActions.DOWN)
    press_input_action(ctx, InputActions.SELECT)

    # The selected index should remain unchanged
    assert ctx.state_manager.get(StateKeys.SELECTED_INDEX) == 0
    assert ctx.navigator.get_active_screen().key == "Empty"

    # The selected index should remain unchanged
    assert "Error in subscriber" not in caplog.text


def test_selecting_settings_opens_the_settings_menu():
    ctx = create_main_menu_context()

    # Settings is the third option of the main menu
    press_input_action(ctx, InputActions.DOWN)
    press_input_action(ctx, InputActions.DOWN)
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen() == settings_screen


def test_back_from_the_settings_menu_returns_to_the_main_menu():
    ctx = create_main_menu_context()
    ctx.navigator.navigate_to(settings_screen.key)

    press_input_action(ctx, InputActions.BACK)

    assert ctx.navigator.get_active_screen() == main_screen


def test_back_to_main_menu_entry_returns_to_the_main_menu():
    ctx = create_main_menu_context()
    ctx.navigator.navigate_to(settings_screen.key)

    # The last option is "Back to Main Menu": UP from the first wraps to it
    press_input_action(ctx, InputActions.UP)
    press_input_action(ctx, InputActions.SELECT)

    assert ctx.navigator.get_active_screen() == main_screen
