from core.event_bus import event_bus

class StateManager():
    def __init__(self, event_bus):
        self._event_bus = event_bus
        self._state = {
            "active_menu": "Main Menu",
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
            self._event_bus.publish(key, value)
        except Exception as e:
            print(f"Error setting state for {key}: {e}")

state_manager = StateManager(event_bus)