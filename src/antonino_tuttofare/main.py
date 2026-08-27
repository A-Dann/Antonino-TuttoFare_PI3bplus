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

def main():
    logger.info("Application started in CLI state-machine mode.")
    current_state = "MAIN_MENU"
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

if __name__ == "__main__":
    main()