import logging

from core.context import AppContext
from core.event_bus import EventBus
from core.events import Events
from core.input_actions import InputActions
from core.input_event import InputEvent
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.state_manager import StateManager
from ui.navigation import Navigator

logging.basicConfig(level=logging.INFO)

def post_test_inputs(event_bus: EventBus) -> None:
    """Temporary: simulates user input until hal/inputs.py exists."""
    sequence = [
        InputActions.DOWN,
        InputActions.SELECT,   # Dual Audio
        InputActions.DOWN,
        InputActions.DOWN,
        InputActions.SELECT,   # Exit
    ]
    for action in sequence:
        event_bus.post(
            Events.INPUT_ACTION,
            InputEvent(input_action=action, source="test"),
        )


def main()-> None:
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    navigator = Navigator(state_manager)
    ctx = AppContext(event_bus, state_manager, navigator)

    ctx.plugin_manager = PluginManager(ctx)
    ctx.plugin_manager.discover()
    ctx.plugin_manager.start_all()
    
    post_test_inputs(event_bus)

    try:
        while state_manager.get(StateKeys.ACTIVE_SCREEN) is not None:
            event_bus.dispatch_next_event()
    except KeyboardInterrupt:
        pass
    except Exception:
        logging.exception("Unexpected error in main loop")
    finally:
        ctx.plugin_manager.stop_all()


if __name__ == "__main__":
    main()