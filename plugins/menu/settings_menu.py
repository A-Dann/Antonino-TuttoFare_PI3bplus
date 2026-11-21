import logging

from ui.screens import MenuItem, MenuScreen

from .language_menu import language_screen

log = logging.getLogger(__name__)

def _action_system_info(ctx):
    log.info("System Info selected")

def _action_configure_wifi(ctx):
    log.info("Configure Wifi selected")

def _action_sync_time_place(ctx):
    log.info("Sync Time & Place selected")

def _action_change_language(ctx):
    log.info("Change Language selected")
    ctx.navigator.navigate_to(language_screen.key)

def _action_back_to_main_menu(ctx):
    log.info("Going back to the parent menu")
    ctx.navigator.go_back()

settings_screen = MenuScreen(
    key="settings",
    title="settings.title",
    options=(
        MenuItem(id="sys_info", label="settings.sys_info"),
        MenuItem(id="configure_wifi", label="settings.configure_wifi"),
        MenuItem(id="sync_time_place", label="settings.sync_time_place"),
        MenuItem(id="change_language", label="settings.change_language"),
        MenuItem(id="back_to_menu", label="settings.back_to_menu"),
    ),
)

settings_actions = {
    "sys_info": _action_system_info,
    "configure_wifi": _action_configure_wifi,
    "sync_time_place": _action_sync_time_place,
    "change_language": _action_change_language,
    "back_to_menu": _action_back_to_main_menu
}
