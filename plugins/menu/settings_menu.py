from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ui.screens import MenuItem, MenuScreen

from .language_menu import language_screen

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.context import AppContext

log = logging.getLogger(__name__)

def _action_system_info(ctx: AppContext) -> None:
    log.info("System Info selected")

def _action_configure_wifi(ctx: AppContext) -> None:
    log.info("Configure Wifi selected")

def _action_sync_time_place(ctx: AppContext) -> None:
    log.info("Sync Time & Place selected")

def _action_change_language(ctx: AppContext) -> None:
    log.info("Change Language selected")
    ctx.navigator.navigate_to(language_screen.key)

def _action_back_to_main_menu(ctx: AppContext) -> None:
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

settings_actions: dict[str, Callable[[AppContext], None]] = {
    "sys_info": _action_system_info,
    "configure_wifi": _action_configure_wifi,
    "sync_time_place": _action_sync_time_place,
    "change_language": _action_change_language,
    "back_to_menu": _action_back_to_main_menu
}
