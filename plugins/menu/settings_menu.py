import logging

from ui.screens import MenuItem, MenuScreen

log = logging.getLogger(__name__)

def _action_system_info(ctx):
    log.info("System Info selected")

def _action_configure_wifi(ctx):
    log.info("Configure Wifi selected")

def _action_sync_time_place(ctx):
    log.info("Sync Time & Place selected")

def _action_change_language(ctx):
    log.info("Change Language selected")

def _action_back_to_main_menu(ctx):
    log.info("Going back to the parent menu")
    ctx.navigator.go_back()

settings_screen = MenuScreen(
    key="settings",
    title="Settings",
    options=[
        MenuItem(id="sys_info", label="System Info"),
        MenuItem(id="configure_wifi", label="Configure Wi-Fi"),
        MenuItem(id="sync_time_place", label="Synchronize Time and Place"),
        MenuItem(id="change_language", label="Change Language"),
        MenuItem(id="back_to_menu", label="Back to Main Menu"),
    ],
)

settings_actions = {
    "sys_info": _action_system_info,
    "configure_wifi": _action_configure_wifi,
    "sync_time_place": _action_sync_time_place,
    "change_language": _action_change_language,
    "back_to_menu": _action_back_to_main_menu
}
