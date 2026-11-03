import logging

from core.context import AppContext
from core.event_bus import EventBus
from core.input_event import InputEvent
from core.input_actions import InputActions
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.events import Events
from core.state_manager import StateManager
from hal.console_display import ConsoleDisplay
from hal.dummy_input import DummyInput
from ui.navigation import Navigator
from ui.renderer import Renderer

logging.basicConfig(level=logging.INFO, filename="app.log", filemode="w", format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", encoding="utf-8")


def main() -> None:
    def _emit(event: InputEvent) -> None:
        event_bus.post(Events.INPUT_ACTION, event)

    sequence = [
        InputActions.DOWN,
        InputActions.SELECT,   # Dual Audio
        InputActions.DOWN,
        InputActions.DOWN,
        InputActions.SELECT,   # Exit
    ]

    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)

    console_display = ConsoleDisplay()
    renderer =  Renderer(event_bus, state_manager, navigator, console_display)
    renderer.start()

    ctx.plugin_manager = PluginManager(ctx)
    ctx.plugin_manager.discover()
    ctx.plugin_manager.start_all()

    dummy_input = DummyInput(sequence, delay=0.5)

    try:
        console_display.start()
        dummy_input.start(_emit)
        while state_manager.get(StateKeys.RUNNING) is True:
            event_bus.dispatch_next_event()
            renderer.render_if_needed()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Unexpected error in main loop")
    finally:
        dummy_input.stop()
        console_display.stop()
        ctx.plugin_manager.stop_all()


if __name__ == "__main__":
    main()