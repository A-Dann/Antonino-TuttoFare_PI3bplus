import logging
from typing import Any

from core.events import Events
from core.state_changed import StateChanged
from core.state_keys import StateKeys

log = logging.getLogger(__name__)

class StateManager:
    def __init__(self, event_bus) -> None:
        self._event_bus = event_bus
        self._state = {
            StateKeys.LANGUAGE: "en",
            StateKeys.ACTIVE_SCREEN: None,
            StateKeys.SELECTED_INDEX: 0,
            StateKeys.AI_AGENT_RUNNING: False,
            StateKeys.WIFI_CONNECTED: False,
            StateKeys.MICROPHONE_CONNECTED: False,
            StateKeys.SPEAKER_CONNECTED: False,
            StateKeys.ANTENNA_CONNECTED: False,
            StateKeys.RUNNING: True,
        }

    def get(self, key) -> Any:
        if not self._is_known(key):
            log.warning("Unknown state key: %s", key)
            return None

        return self._state.get(key)

    def set(self, key, value) -> None:
        if not self._is_known(key):
            log.warning("Unknown state key: %s", key)
            return

        if self._state.get(key) == value:
            return

        self._state[key] = value
        self._event_bus.publish(Events.STATE_CHANGED, StateChanged(key, value))

    def _is_known(self, key) -> bool:
        return key in self._state
