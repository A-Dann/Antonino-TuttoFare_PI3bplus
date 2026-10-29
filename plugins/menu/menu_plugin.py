# plugins/menu/menu_plugin.py
import logging

from core.events import Events
from core.interfaces.plugin_interface import Plugin
from core.state_keys import StateKeys
from ui.navigation import execute_action, get_active_screen, register_screen
from ui.screens import MenuScreen

from .main_menu import main_screen, main_actions

log = logging.getLogger(__name__)

class MenuPlugin(Plugin):
    def start(self, ctx) -> None:
        log.info("Starting MenuPlugin")
        self._ctx = ctx

        # Register the main menu screen and actions
        register_screen(main_screen, main_actions)
        ctx.event_bus.subscribe(Events.INPUT_ACTION, self._handle_input_action)
        ctx.state_manager.set(StateKeys.ACTIVE_SCREEN, main_screen.key)

    def _handle_input_action(self, event) -> None:
        screen = get_active_screen(self._ctx.state_manager)
        if not isinstance(screen, MenuScreen):
            return  # Not a menu screen, ignore

        action = event.get("action")
        if action == "up":
            self._move(screen, -1)
        elif action == "down":
            self._move(screen, 1)
        elif action == "select":
            selected_option = screen.options[screen.selected_option]
            execute_action(self._ctx.event_bus, self._ctx.state_manager, selected_option.id)

    def _move(self, screen: MenuScreen, step: int) -> None:
        screen.selected_option = (screen.selected_option + step) % len(screen.options)
        self._ctx.event_bus.publish(Events.UI_UPDATE, {"screen": screen.key})