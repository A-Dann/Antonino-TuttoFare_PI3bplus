"""
Module dedicated to managing the global application state in a thread-safe manner.
"""

import threading
import logging

logger = logging.getLogger(__name__)

current_state = "MAIN_MENU"
state_lock = threading.Lock()
state_changed_event = threading.Event()

VALID_STATES = [
    # Main Menu & core modes
    "MAIN_MENU",
    "DESKTOP_MODE",
    "DUAL_AUDIO",
    "TURN_OFF",
    "EXIT",
    
    # Settings & sub-states
    "SETTINGS",
    "SYSTEM_INFO",
    "WIFI_MENU",
    "SYNC_TIME_AND_PLACE",
    "CHANGE_LANGUAGE",
    
    # Wi-Fi sub-states (Screens/Views)
    "WIFI_STATUS",
    "WIFI_SCAN",
    "WIFI_SAVED",
    "WIFI_REMOVE"
]

def get_current_state() -> str:
    """Thread-safe getter for the current application state."""
    with state_lock:
        return current_state

def set_current_state(target_state: str) -> str:
    """Thread-safe function to change the application state.
    
    Args:
        target_state: The exact string identifier of the target state.
    """
    global current_state
    if target_state not in VALID_STATES:
        logger.warning(f"Attempted to switch to an invalid state: {target_state}")
        return f"Error: State '{target_state}' does not exist."

    with state_lock:
        logger.info(f"State changed from {current_state} to {target_state}")
        current_state = target_state
        
    state_changed_event.set()
    return f"State successfully changed to {target_state}"