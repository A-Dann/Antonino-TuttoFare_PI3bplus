import logging

from core.context import AppContext
from core.event_bus import EventBus
from core.input_event import InputEvent
from core.input_actions import InputActions
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.events import Events
from core.state_manager import StateManager
from hal.dummy_input import DummyInput
from ui.navigation import Navigator

logging.basicConfig(level=logging.INFO)


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

    ctx.plugin_manager = PluginManager(ctx)
    ctx.plugin_manager.discover()
    ctx.plugin_manager.start_all()

    dummy_input = DummyInput(sequence)

    try:
        dummy_input.start(_emit)
        while state_manager.get(StateKeys.ACTIVE_SCREEN) is not None:
            event_bus.dispatch_next_event()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Unexpected error in main loop")
    finally:
        dummy_input.stop()
        ctx.plugin_manager.stop_all()


if __name__ == "__main__":
    main()