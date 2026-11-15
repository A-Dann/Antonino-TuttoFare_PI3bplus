from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.context import AppContext
from core.state_keys import StateKeys
from ui.screens import Screen

if TYPE_CHECKING:
    from core.state_manager import StateManager

log = logging.getLogger(__name__)
ActionMap = dict[str, Callable[[AppContext], None]]

class Navigator:
    def __init__(self, state_manager: StateManager) -> None:
        self._state_manager = state_manager
        self._screens: dict[str, Screen] = {}
        self._parents: dict[str, str] = {}
        self._actions: dict[str, ActionMap] = {}

    def register_screen(
        self,
        screen: Screen,
        actions: ActionMap | None = None,
        *,
        parent: str | None = None,
    ) -> None:

        if screen.key in self._screens:
            log.warning("Screen with key %s is already registered.", screen.key)
            return

        self._screens[screen.key] = screen
        if parent is not None:
            self._parents[screen.key] = parent
        if actions:
            self._actions[screen.key] = actions

    def get_active_screen(self) -> Screen | None:
        current_key = self._state_manager.get(StateKeys.ACTIVE_SCREEN)
        return self._screens.get(current_key)

    def go_back(self) -> None:
        current_key = self._state_manager.get(StateKeys.ACTIVE_SCREEN)
        parent_key = self._parents.get(current_key)

        if parent_key is None:
            log.debug("Cannot go back, screen has no parent.")
            return

        self.navigate_to(parent_key)

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
