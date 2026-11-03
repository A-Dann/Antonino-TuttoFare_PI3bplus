from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from core.state_keys import StateKeys

if TYPE_CHECKING:
    from core.context import AppContext
    from core.state_manager import StateManager
    from ui.screens import MenuScreen

log = logging.getLogger(__name__)

class Navigator:
    def __init__(self, state_manager: StateManager) -> None:
        self._state_manager = state_manager
        self._screens = {}
        self._actions = {}

    def register_screen(self, screen, actions=None) -> None:
        if screen.key in self._screens:
            log.warning("Screen with key %s is already registered.", screen.key)
            return
        
        self._screens[screen.key] = screen
        if actions:
            self._actions[screen.key] = actions

    def get_active_screen(self) -> MenuScreen | None:
        current_key = self._state_manager.get(StateKeys.ACTIVE_SCREEN)
        return self._screens.get(current_key)

    def navigate_to(self, screen_key: str) -> None:
        if screen_key not in self._screens:
            log.warning("Attempted to navigate to unregistered screen: %s", screen_key)
            return
        if self._state_manager.get(StateKeys.ACTIVE_SCREEN) == screen_key:
            log.debug("Already on screen: %s", screen_key)
            return

        self._state_manager.set(StateKeys.SELECTED_INDEX, 0)  # Reset selected index when navigating to a new screen
        self._state_manager.set(StateKeys.ACTIVE_SCREEN, screen_key)

    def execute_action(self, ctx: AppContext, action_id: str) -> None:
        current_key = self._state_manager.get(StateKeys.ACTIVE_SCREEN)
        actions = self._actions.get(current_key, {})

        action = actions.get(action_id)
        if action:
            action(ctx)
        else:
            log.warning("No action found for id: %s on screen: %s", action_id, current_key)