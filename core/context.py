from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from core.state_manager import StateManager
    from core.plugin_manager import PluginManager
    from ui.navigation import Navigator

class AppContext:
    def __init__(self, event_bus: EventBus, state_manager: StateManager, navigator: Navigator, plugin_manager: PluginManager | None = None):
        self.event_bus = event_bus
        self.state_manager = state_manager
        self.navigator = navigator
        self.plugin_manager = plugin_manager