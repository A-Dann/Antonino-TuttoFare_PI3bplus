import logging

from core.state_keys import StateKeys
from ui.screens import MenuItem, MenuScreen

log = logging.getLogger(__name__)

def _make_language_action(language):
    def action(ctx):
        log.info("Language changed to %s", language)
        ctx.state_manager.set(StateKeys.LANGUAGE, language)
    return action

def _action_back_to_settings(ctx):
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

language_actions = {
    "en": _make_language_action("en"),
    "it": _make_language_action("it"),
    "es": _make_language_action("es"),
    "back": _action_back_to_settings,
}
