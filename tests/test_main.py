from core.events import Events
from core.input_actions import InputActions
from core.input_event import InputEvent
from core.interfaces.display_interface import DisplayInterface
from core.state_keys import StateKeys
from main import build_app, run_one_turn

UP, DOWN, SELECT, BACK = InputActions.UP, InputActions.DOWN, InputActions.SELECT, InputActions.BACK

# --- helpers ---------------------------------------------------------------

class DummyDisplay(DisplayInterface):
    name = "dummy"

    def __init__(self):
        self.draws = []

    def start(self) -> None:
        pass

    def show_menu(self, title: str, options: list[str], selected_index: int) -> None:
        self.draws.append((title, options, selected_index))

    def clear_screen(self) -> None:
        pass

    def stop(self) -> None:
        pass


def start_app():
    """Build the real app with a fake display and draw the first screen."""
    display = DummyDisplay()
    app = build_app(display)
    app.renderer.render_if_needed()
    return app, display


def press(app, *actions):
    """Simulate the keys: post each action as a device would, then run one loop turn."""
    for action in actions:
        app.ctx.event_bus.post(Events.INPUT_ACTION, InputEvent(action, "test"))
        run_one_turn(app)


# --- tests -----------------------------------------------------------------

def test_the_app_starts_on_the_main_menu_in_english():
    _, display = start_app()

    assert display.draws == [("MAIN MENU", ["Desktop Mode", "Dual Audio", "Settings", "Exit"], 0)]


def test_select_on_settings_opens_the_settings_menu():
    app, display = start_app()

    press(app, DOWN, DOWN, SELECT)

    title, _, selected_index = display.draws[-1]
    assert title == "SETTINGS"
    assert selected_index == 0


def test_back_returns_to_the_main_menu():
    app, display = start_app()
    press(app, DOWN, DOWN, SELECT)

    press(app, BACK)

    assert display.draws[-1][0] == "MAIN MENU"


def test_choosing_a_language_translates_the_menus():
    app, display = start_app()

    # Main menu -> Settings -> Change Language -> Italiano
    press(app, DOWN, DOWN, SELECT)
    press(app, DOWN, DOWN, DOWN, SELECT)
    press(app, DOWN, SELECT)

    assert display.draws[-1][0] == "LINGUA"

    press(app, BACK, BACK)

    assert display.draws[-1] == (
        "MENU PRINCIPALE",
        ["Modalità Desktop", "Audio Duale", "Impostazioni", "Esci"],
        0,
    )


def test_exit_stops_the_main_loop():
    app, _ = start_app()

    press(app, DOWN, DOWN, DOWN, SELECT)

    assert app.ctx.state_manager.get(StateKeys.RUNNING) is False
