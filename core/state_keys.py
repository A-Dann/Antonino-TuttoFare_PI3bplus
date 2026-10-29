from enum import Enum

class StateKeys(str, Enum):
    ACTIVE_SCREEN = "active_screen"
    AI_AGENT_RUNNING = "ai_agent_running"
    WIFI_CONNECTED = "wifi_connected"
    MICROPHONE_CONNECTED = "microphone_connected"
    SPEAKER_CONNECTED = "speaker_connected"
    ANTENNA_CONNECTED = "antenna_connected"