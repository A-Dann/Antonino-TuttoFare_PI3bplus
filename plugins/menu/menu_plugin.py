# plugins/menu/menu_plugin.py
from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from core.events import Events
from core.input_actions import InputActions
from core.interfaces.plugin_interface import Plugin
from core.state_keys import StateKeys
from ui.screens import MenuScreen

from .main_menu import main_screen, main_actions

if TYPE_CHECKING:
    from core.context import AppContext

log = logging.getLogger(__name__)

class MenuPlugin(Plugin):
    def start(self, ctx: AppContext) -> None:
        log.info("Starting MenuPlugin")
        self._ctx = ctx

        # Register the main menu screen and actions
        self._ctx.navigator.register_screen(main_screen, main_actions)
        ctx.event_bus.subscribe(Events.INPUT_ACTION, self._handle_input_action)
        ctx.navigator.navigate_to(main_screen.key)

    def _handle_input_action(self, event) -> None:
        screen = self._ctx.navigator.get_active_screen()
        if not isinstance(screen, MenuScreen):
            return  # Not a menu screen, ignore
        if len(screen.options) == 0:
            return  # No options to move through

        action = event.input_action
        if action == InputActions.UP:
            self._move(screen, -1)
        elif action == InputActions.DOWN:
            self._move(screen, 1)
        elif action == InputActions.SELECT:
            selected_option = screen.options[self._ctx.state_manager.get(StateKeys.SELECTED_INDEX)]
            self._ctx.navigator.execute_action(self._ctx, selected_option.id)

    def _move(self, screen: MenuScreen, step: int) -> None:
        selected_index = (self._ctx.state_manager.get(StateKeys.SELECTED_INDEX) + step) % len(screen.options)
        self._ctx.state_manager.set(StateKeys.SELECTED_INDEX, selected_index)