import logging

from core.state_keys import StateKeys
from ui.screens import MenuItem, MenuScreen

log = logging.getLogger(__name__)

def _action_desktop_mode(ctx):
    log.info("Desktop Mode selected")

def _action_dual_audio(ctx):
    log.info("Dual Audio selected")

def _action_settings(ctx):
    log.info("Settings selected")

def _action_exit(ctx):
    log.info("Turning off application")
    ctx.state_manager.set(StateKeys.RUNNING, False)

main_screen = MenuScreen(
    key="main",
    title="Main Menu",
    options=[
        MenuItem(id="desktop", label="Desktop Mode"),
        MenuItem(id="dual_audio", label="Dual Audio"),
        MenuItem(id="settings", label="Settings"),
        MenuItem(id="exit", label="Exit")
    ],
)

main_actions = {
    "desktop": _action_desktop_mode,
    "dual_audio": _action_dual_audio,
    "settings": _action_settings,
    "exit": _action_exit
}
