import logging

from ui.screens import MenuItem, MenuScreen

log = logging.getLogger(__name__)

def _action_desktop_mode(event_bus, state_manager):
    log.info("Desktop Mode selected")

def _action_dual_audio(event_bus, state_manager):
    log.info("Dual Audio selected")

def _action_settings(event_bus, state_manager):
    log.info("Settings selected")

def _action_exit(event_bus, state_manager):
    log.info("Turning off application")
    state_manager.set("active_screen", None)

main_screen = MenuScreen(
    key="Main",
    title="Main Menu",
    options=[
        MenuItem(id="desktop", label="Desktop Mode"),
        MenuItem(id="dual_audio", label="Dual Audio"),
        MenuItem(id="settings", label="Settings"),
        MenuItem(id="exit", label="Exit")
    ],
    selected_option=0
)

main_actions = {
    "desktop": _action_desktop_mode,
    "dual_audio": _action_dual_audio,
    "settings": _action_settings,
    "exit": _action_exit
}