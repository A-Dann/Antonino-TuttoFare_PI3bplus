from typing import Protocol, Any

class PluginInterface(Protocol):
    """Standard contract for each plugin."""
    
    def init(self, event_bus: Any, state_manager: Any) -> None:
        """Initializes the plugin with the dipendencies."""