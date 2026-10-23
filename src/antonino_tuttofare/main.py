#!/usr/bin/env python3
"""
Main entry point for the logic/CLI branch using a state machine structure.
"""

import builtins
import logging

from dotenv import load_dotenv
# Upload environment variables from .env file
load_dotenv()

from antonino_tuttofare import menu, settings, state
from antonino_tuttofare.menu_modules import desktop_mode, dual_audio, turn_off
from antonino_tuttofare.settings_modules import wifi_menu, change_language, sync_time_and_place, system_info
from antonino_tuttofare.utility.i18n import t
from antonino_tuttofare.utility.input_utils import universal_input, StateChangedInterrupt

logger = logging.getLogger(__name__)

# State handler registry mapping states to their respective runner modules
STATE_HANDLERS = {
    # Main Menu & core modes
    "MAIN_MENU": menu.run_cli_state,
    "DESKTOP_MODE": desktop_mode.run_cli_state,
    "DUAL_AUDIO": dual_audio.run_cli_state,
    "SETTINGS": settings.run_cli_state,
    "SYSTEM_INFO": system_info.run_cli_state,

    # Settings & sub-states

    # Wi-Fi Menu & Sub-states
    "WIFI_MENU": wifi_menu.run_cli_state,
    "WIFI_STATUS": wifi_menu.run_cli_state,
    "WIFI_SCAN": wifi_menu.run_cli_state,
    "WIFI_SAVED": wifi_menu.run_cli_state,
    "WIFI_REMOVE": wifi_menu.run_cli_state,
    
    "SYNC_TIME_AND_PLACE": sync_time_and_place.run_cli_state,
    "CHANGE_LANGUAGE": change_language.run_cli_state,
    "TURN_OFF": turn_off.run_cli_state,
}

# Override builtins.input globally to make all menu inputs instantly reactive to voice commands
builtins.input = universal_input


def main():
    """Main application loop managing state machine transitions reactively."""
    logger.info("Application started in CLI state-machine mode.")
    selected_index = 0
    running = True
    
    while running:
        active_state = state.get_current_state()
        previous_state = active_state
        state.state_changed_event.clear()

        if active_state == "EXIT":
            logger.info("Exiting application.")
            running = False
            break

        handler = STATE_HANDLERS.get(active_state)
        if handler:
            try:
                # Execute the current state handler; any internal input() call is now interruptible
                next_state, selected_index = handler(selected_index)
                state.set_current_state(next_state)
            except StateChangedInterrupt:
                # Instantly abort the current menu handler when an asynchronous voice command changes the state
                logger.info("Menu interrupted by asynchronous voice state change.")
                selected_index = 0
                continue
        else:
            logger.error(f"No handler found for state: {active_state}")
            state.set_current_state("MAIN_MENU")

        if state.get_current_state() != previous_state:
            selected_index = 0


def change_state(target_state: str) -> str:
    """Wrapper function to change state for external tool compatibility."""
    return state.set_current_state(target_state)


def get_current_state() -> str:
    """Wrapper function to get current state."""
    return state.get_current_state()


if __name__ == "__main__":
    main()