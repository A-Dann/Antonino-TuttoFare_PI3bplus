import logging

log = logging.getLogger(__name__)

class StateManager():
    def __init__(self, event_bus):
        self._event_bus = event_bus
        self._state = {
            "active_screen": None,
            "ai_agent_running": False,
            "wifi_connected" : False,
            "microphone_connected": False,
            "speaker_connected": False,
            "antenna_connected": False,
        }

    def get(self, key):
        return self._state.get(key)

    def set(self, key, value):
        try:  
            self._state[key] = value
            self._event_bus.publish("STATE_CHANGED", {"key": key, "value": value})
        except Exception as e:
            log.error(f"Error setting state for {key}: {e}")