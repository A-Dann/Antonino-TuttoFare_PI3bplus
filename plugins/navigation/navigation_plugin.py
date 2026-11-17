from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.events import Events
from core.input_actions import InputActions
from core.interfaces.plugin_interface import Plugin

if TYPE_CHECKING:
    from core.context import AppContext
    from core.input_event import InputEvent

log = logging.getLogger(__name__)

class NavigationPlugin(Plugin):
    def start(self, ctx: AppContext) -> None:
        log.info("Starting NavigationPlugin")
        self._ctx = ctx

        ctx.event_bus.subscribe(Events.INPUT_ACTION, self._handle_input_action)

    def _handle_input_action(self, event: InputEvent) -> None:
        if event.action == InputActions.BACK:
            self._ctx.navigator.go_back()
