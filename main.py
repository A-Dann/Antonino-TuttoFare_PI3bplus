import time
from core.event_bus import EventBus
from core.state_manager import StateManager
from core.plugin_manager import PluginManager

class AppContext:
    def __init__(self, event_bus, state_manager):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.plugin_manager = PluginManager(self)

def main():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    
    ctx = AppContext(event_bus, state_manager)
    
    # 3. Avvio dei plugin e loop principale (lo completiamo al prossimo step)
    print("Sistema avviato.")

if __name__ == "__main__":
    main()