import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import NamedTuple

from core.context import AppContext
from core.event_bus import EventBus
from core.events import Events
from core.input_event import InputEvent
from core.interfaces.display_interface import DisplayInterface
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.state_manager import StateManager
from core.translator import Translator
from hal.display.console_display import ConsoleDisplay
from hal.input.evdev_input import EvdevInput
from hal.input.input_manager import InputManager
from hal.input.keyboard_input import KeyboardInput
from hal.input.terminal_input import TerminalInput
from plugins.menu.main_menu import main_screen
from ui.navigation import Navigator
from ui.renderer import Renderer

LOG_FILE = "app.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 3

LOCALES_DIR = Path(__file__).parent / "locales"

SCAN_INTERVAL = 2.0


class App(NamedTuple):
    """The parts of the app that do not depend on the hardware."""
    ctx: AppContext
    renderer: Renderer
    plugin_manager: PluginManager


def setup_logging() -> None:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def build_app(display: DisplayInterface) -> App:
    """Create the services, start the plugins and choose the first screen.

    It does not touch the input devices, so the tests can use it with a fake display.
    """
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    translator = Translator(state_manager, LOCALES_DIR)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)

    renderer = Renderer(event_bus, state_manager, translator, navigator, display)
    renderer.start()

    plugin_manager = PluginManager(ctx)
    ctx.plugin_manager = plugin_manager
    plugin_manager.discover()
    plugin_manager.start_all()

    navigator.navigate_to(main_screen.key)

    return App(ctx, renderer, plugin_manager)


def run_one_turn(app: App) -> None:
    """One turn of the main loop: handle one event, then redraw if something changed."""
    app.ctx.event_bus.dispatch_next_event()
    app.renderer.render_if_needed()


def main() -> None:
    setup_logging()

    driver_classes: list[type[EvdevInput]] = [
        KeyboardInput,
    ]

    console_display = ConsoleDisplay()
    app = build_app(console_display)

    def _emit(event: InputEvent) -> None:
        app.ctx.event_bus.post(Events.INPUT_ACTION, event)

    input_manager = InputManager(_emit, driver_classes, SCAN_INTERVAL)
    terminal_input = TerminalInput()

    try:
        console_display.start()
        input_manager.start()
        terminal_input.start(_emit)

        while app.ctx.state_manager.get(StateKeys.RUNNING) is True:
            run_one_turn(app)
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Unexpected error in main loop")
    finally:
        terminal_input.stop()
        input_manager.stop()
        console_display.stop()
        app.plugin_manager.stop_all()


if __name__ == "__main__":
    main()
