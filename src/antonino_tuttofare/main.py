#!/usr/bin/env python3
"""
Main entry point for the logic/CLI branch using a state machine structure.
"""

import logging
from antonino_tuttofare import menu, settings
from antonino_tuttofare.menu_modules import desktop_mode, dual_audio, turn_off
from antonino_tuttofare.settings_modules import wifi_menu, change_language, sync_time_and_place, system_info
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)
current_state = "MAIN_MENU"

VALID_STATES = [
    "MAIN_MENU",
    "DESKTOP_MODE",
    "DUAL_AUDIO",
    "SETTINGS",
    "SYSTEM_INFO",
    "WIFI_MENU",
    "SYNC_TIME_AND_PLACE",
    "CHANGE_LANGUAGE",
    "TURN_OFF",
    "EXIT"
]

def main():
    logger.info("Application started in CLI state-machine mode.")
    global current_state
    selected_index = 0
    running = True
    while running:
        previous_state = current_state

        if current_state == "MAIN_MENU":
            current_state, selected_index = menu.run_cli_state(selected_index)

        elif current_state == "DESKTOP_MODE":
            current_state, selected_index = desktop_mode.run_cli_state(selected_index)

        elif current_state == "DUAL_AUDIO":
            current_state, selected_index = dual_audio.run_cli_state(selected_index)

        elif current_state == "SETTINGS":
            current_state, selected_index = settings.run_cli_state(selected_index)
        
        elif current_state == "SYSTEM_INFO":
            current_state, selected_index = system_info.run_cli_state(selected_index)

        elif current_state == "WIFI_MENU":
            current_state, selected_index = wifi_menu.run_cli_state(selected_index)
            
        elif current_state == "SYNC_TIME_AND_PLACE":
            current_state, selected_index = sync_time_and_place.run_cli_state(selected_index)            

        elif current_state == "CHANGE_LANGUAGE":
            current_state, selected_index = change_language.run_cli_state(selected_index)

        elif current_state == "TURN_OFF":
            current_state, selected_index = turn_off.run_cli_state(selected_index)

        elif current_state == "EXIT":
            logger.info("Exiting application.")
            running = False

        if current_state != previous_state:
            selected_index = 0

def get_current_state():
    return current_state

def change_state(target_state: str) -> str:
    """Changes the application navigation state.
    
    Args:
        target_state: The exact string identifier of the target state (e.g., MAIN_MENU, SETTINGS, WIFI_MENU, DESKTOP_MODE).
    """
    if target_state not in VALID_STATES:
        logger.warning(f"AI tried to switch to an invalid state: {target_state}")
        return f"Error: State '{target_state}' does not exist. Choose from: {', '.join(VALID_STATES)}"

    logger.info(f"Tool executed: changing state to {target_state}")
    main.current_state = target_state
    return f"State successfully changed to {target_state}"

if __name__ == "__main__":
    main()