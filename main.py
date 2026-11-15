import logging

from core.context import AppContext
from core.event_bus import EventBus
from core.events import Events
from core.input_event import InputEvent
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.state_manager import StateManager
from hal.display.console_display import ConsoleDisplay
from hal.input.evdev_input import EvdevInput
from hal.input.input_manager import InputManager
from hal.input.keyboard_input import KeyboardInput
from hal.input.terminal_input import TerminalInput
from ui.navigation import Navigator
from ui.renderer import Renderer

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    encoding="utf-8"
)

SCAN_INTERVAL = 2.0

def main() -> None:
    def _emit(event: InputEvent) -> None:
        event_bus.post(Events.INPUT_ACTION, event)

    driver_classes: list[type[EvdevInput]] = [
        KeyboardInput,
    ]

    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)

    input_manager = InputManager(_emit, driver_classes, SCAN_INTERVAL)
    console_display = ConsoleDisplay()
    renderer = Renderer(event_bus, state_manager, navigator, console_display)
    renderer.start()

    ctx.plugin_manager = PluginManager(ctx)
    ctx.plugin_manager.discover()
    ctx.plugin_manager.start_all()

    terminal_input = TerminalInput()

    try:
        console_display.start()
        input_manager.start()
        terminal_input.start(_emit)

        while state_manager.get(StateKeys.RUNNING) is True:
            event_bus.dispatch_next_event()
            renderer.render_if_needed()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Unexpected error in main loop")
    finally:
        terminal_input.stop()
        input_manager.stop()
        console_display.stop()
        ctx.plugin_manager.stop_all()


if __name__ == "__main__":
    main()
