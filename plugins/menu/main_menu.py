import logging

from core.state_keys import StateKeys
from ui.screens import MenuItem, MenuScreen

from .settings_menu import settings_screen

log = logging.getLogger(__name__)

def _action_desktop_mode(ctx):
    log.info("Desktop Mode selected")

def _action_dual_audio(ctx):
    log.info("Dual Audio selected")

def _action_settings(ctx):
    log.info("Settings selected")
    ctx.navigator.navigate_to(settings_screen.key)

def _action_exit(ctx):
    log.info("Turning off application")
    ctx.state_manager.set(StateKeys.RUNNING, False)

main_screen = MenuScreen(
    key="main",
    title="main.title",
    options=(
        MenuItem(id="desktop_mode", label="main.desktop_mode"),
        MenuItem(id="dual_audio", label="main.dual_audio"),
        MenuItem(id="settings", label="main.settings"),
        MenuItem(id="exit", label="main.exit"),
    ),
)

main_actions = {
    "desktop_mode": _action_desktop_mode,
    "dual_audio": _action_dual_audio,
    "settings": _action_settings,
    "exit": _action_exit
}
