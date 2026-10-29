import logging
import time

from core.events import Events
from core.state_keys import StateKeys
from core.event_bus import EventBus
from core.state_manager import StateManager
from core.plugin_manager import PluginManager

logging.basicConfig(level=logging.INFO)


class AppContext:
    def __init__(self, event_bus, state_manager):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.plugin_manager = None


def main():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    ctx = AppContext(event_bus, state_manager)

    ctx.plugin_manager = PluginManager(ctx)
    ctx.plugin_manager.discover()
    ctx.plugin_manager.start_all()

    # prova provvisoria, da togliere quando esisterà hal/inputs.py
    event_bus.publish(Events.INPUT_ACTION, {"action": "down"})
    event_bus.publish(Events.INPUT_ACTION, {"action": "select"})
    
    try:
        while state_manager.get(StateKeys.ACTIVE_SCREEN) is not None:
            time.sleep(0.1)  # provvisorio: qui andrà il main loop vero
    except KeyboardInterrupt:
        pass
    finally:
        ctx.plugin_manager.stop_all()


if __name__ == "__main__":
    main()