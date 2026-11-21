from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.state_keys import StateKeys
from ui.screens import MenuItem, MenuScreen

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.context import AppContext

log = logging.getLogger(__name__)

def _make_language_action(language: str) -> Callable[[AppContext], None]:
    def action(ctx: AppContext) -> None:
        log.info("Language changed to %s", language)
        ctx.state_manager.set(StateKeys.LANGUAGE, language)
    return action

def _action_back_to_settings(ctx: AppContext) -> None:
    log.info("Going back to the parent menu")
    ctx.navigator.go_back()

language_screen = MenuScreen(
    key="language",
    title="language.title",
    options=(
        MenuItem(id="en", label="language.en"),
        MenuItem(id="it", label="language.it"),
        MenuItem(id="es", label="language.es"),
        MenuItem(id="back", label="language.back"),
    ),
)

language_actions: dict[str, Callable[[AppContext], None]] = {
    "en": _make_language_action("en"),
    "it": _make_language_action("it"),
    "es": _make_language_action("es"),
    "back": _action_back_to_settings,
}
