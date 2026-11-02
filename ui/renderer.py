from __future__ import annotations
import logging
from typing import TYPE_CHECKING
from core.events import Events
from core.state_keys import StateKeys
from ui.screens import MenuScreen

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from core.state_manager import StateManager
    from ui.navigation import Navigator
    from hal.display_interface import DisplayInterface

log = logging.getLogger(__name__)

class Renderer:
    def __init__(self, event_bus: EventBus, state_manager: StateManager, navigator: Navigator, display: DisplayInterface) -> None:
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._navigator = navigator
        self._display = display

        self._need_redraw = True
        self._draw_functions = {
            MenuScreen: self._draw_menu,
        }
        
    def start(self) -> None:
        self._event_bus.subscribe(Events.STATE_CHANGED, self._handle_event)

    def _handle_event(self, data: dict) -> None:
        key = data.get("key")
        if key in [StateKeys.ACTIVE_SCREEN, StateKeys.SELECTED_INDEX]:
            self._need_redraw = True

    def render_if_needed(self) -> None:
        if not self._need_redraw:
            return
        self._need_redraw = False
        active_screen = self._navigator.get_active_screen()
        
        if active_screen is None:
            return
        screen_type = type(active_screen)

        if screen_type not in self._draw_functions:
            log.warning("No render function registered for screen type: %s", screen_type)
            return

        selected_index = self._state_manager.get(StateKeys.SELECTED_INDEX)
        render_function = self._draw_functions[screen_type]
        render_function(active_screen, selected_index)

    def _draw_menu(self, screen, selected_index: int) -> None:
        options = [option.label for option in screen.options]
        self._display.show_menu(screen.title, options, selected_index)