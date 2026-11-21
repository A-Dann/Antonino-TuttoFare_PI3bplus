import json

from core.event_bus import EventBus
from core.interfaces.display_interface import DisplayInterface
from core.state_keys import StateKeys
from core.state_manager import StateManager
from core.translator import Translator
from ui.navigation import Navigator
from ui.renderer import Renderer
from ui.screens import MenuItem, MenuScreen, Screen

# --- helper section ---

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


LOCALES = {
    "en": {"test": {"title": "Test Screen", "a": "A", "b": "B"}},
    "it": {"test": {"title": "Schermata di prova", "a": "Uno", "b": "Due"}},
}


def _make_translator(directory, state_manager):
    for language, messages in LOCALES.items():
        (directory / f"{language}.json").write_text(json.dumps(messages), encoding="utf-8")
    return Translator(state_manager, directory)


def _renderer_initialization(tmp_path):

    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    translator = _make_translator(tmp_path, state_manager)
    navigator = Navigator(state_manager)
    dummy_display = DummyDisplay()

    renderer = Renderer(event_bus, state_manager, translator, navigator, dummy_display)
    renderer.start()

    navigator.register_screen(
        screen=MenuScreen(
            key="test_screen",
            title="test.title",
            options=(MenuItem("a", "test.a"), MenuItem("b", "test.b"))
        )
    )
    navigator.navigate_to("test_screen")

    return renderer, dummy_display, state_manager, navigator


# --- test section ---

def test_first_render_draws_without_any_change(tmp_path):
    renderer, dummy_display, _, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    assert dummy_display.draws == [("Test Screen", ["A", "B"], 0)]


def test_render_draws_selected_index_after_move(tmp_path):
    renderer, dummy_display, state_manager, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    # Change selected index
    state_manager.set(StateKeys.SELECTED_INDEX, 1)
    renderer.render_if_needed()

    assert dummy_display.draws == [
        ("Test Screen", ["A", "B"], 0),  # First render
        ("Test Screen", ["A", "B"], 1)   # Second render after changing selected index
    ]


def test_render_does_not_draw_again_without_changes(tmp_path):
    renderer, dummy_display, _, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    renderer.render_if_needed() # Call render again without any state change

    assert dummy_display.draws == [("Test Screen", ["A", "B"], 0)]


def test_render_draws_only_once_for_multiple_changes(tmp_path):
    renderer, dummy_display, state_manager, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    # Change selected index multiple times
    state_manager.set(StateKeys.SELECTED_INDEX, 1)
    state_manager.set(StateKeys.SELECTED_INDEX, 0)
    state_manager.set(StateKeys.SELECTED_INDEX, 1)

    renderer.render_if_needed()

    assert dummy_display.draws == [
        ("Test Screen", ["A", "B"], 0),  # First render
        ("Test Screen", ["A", "B"], 1)   # Second render after the last change
    ]


def test_render_does_not_draw_for_unrelated_state_changes(tmp_path):
    renderer, dummy_display, state_manager, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    state_manager.set(StateKeys.MICROPHONE_CONNECTED, True)
    renderer.render_if_needed()  # Render after unrelated change

    assert dummy_display.draws == [("Test Screen", ["A", "B"], 0)]


def test_render_does_not_draw_without_active_screen(tmp_path, caplog):
    renderer, dummy_display, state_manager, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    state_manager.set(StateKeys.ACTIVE_SCREEN, None) # Remove active screen

    with caplog.at_level("WARNING"):
        renderer.render_if_needed()

    assert dummy_display.draws == [("Test Screen", ["A", "B"], 0)]  # No new draw should occur
    assert "No render function registered" not in caplog.text


def test_render_does_not_draw_for_unregistered_screen_type(tmp_path, caplog):
    renderer, dummy_display, _, navigator = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    # Create a new screen type that is not registered in the draw functions
    class UnregisteredScreen(Screen):
        pass

    unregistered_screen = UnregisteredScreen(key="unregistered_screen")
    navigator.register_screen(unregistered_screen)
    navigator.navigate_to("unregistered_screen")

    with caplog.at_level("WARNING"):
        renderer.render_if_needed()

    assert dummy_display.draws == [("Test Screen", ["A", "B"], 0)]  # No new draw should occur
    assert "No render function registered" in caplog.text


def test_render_draws_again_in_the_new_language_when_the_language_changes(tmp_path):
    renderer, dummy_display, state_manager, _ = _renderer_initialization(tmp_path)
    renderer.render_if_needed()

    state_manager.set(StateKeys.LANGUAGE, "it")
    renderer.render_if_needed()

    assert dummy_display.draws == [
        ("Test Screen", ["A", "B"], 0),               # English, the default
        ("Schermata di prova", ["Uno", "Due"], 0),    # redrawn in Italian
    ]
