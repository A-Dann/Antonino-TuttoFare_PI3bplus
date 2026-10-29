import logging

from core.events import Events
from core.state_keys import StateKeys

log = logging.getLogger(__name__)

class StateManager():
    def __init__(self, event_bus):
        self._event_bus = event_bus
        self._state = {
            StateKeys.ACTIVE_SCREEN: None,
            StateKeys.AI_AGENT_RUNNING: False,
            StateKeys.WIFI_CONNECTED: False,
            StateKeys.MICROPHONE_CONNECTED: False,
            StateKeys.SPEAKER_CONNECTED: False,
            StateKeys.ANTENNA_CONNECTED: False,
        }

    def get(self, key):
        return self._state.get(key)

    def set(self, key, value):
        if self._state.get(key) == value:
            return
        
        self._state[key] = value
        self._event_bus.publish(Events.STATE_CHANGES, {"key": key, "value": value})