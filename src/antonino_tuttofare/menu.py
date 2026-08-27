#!/usr/bin/env python3
"""
Main Menu Module (CLI State Version)

This module serves as the primary entry point and main menu loop of the application
adapted for the state machine architecture, allowing users to navigate via terminal inputs.
"""

import logging
from antonino_tuttofare.menu_modules import ai_agent
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run_cli_state(selected_index=0):
    """
    Renders the main menu once in the terminal, processes a single choice input,
    and returns the next application state and selected index.
    """
    print(f"\n--- {t('menu_title')} ---")
    print(f"1. {t('menu_desktop_mode')}")
    print(f"2. {t('menu_dual_audio')}")
    if not ai_agent.is_running():
        print(f"3. {t('Start_ai_agent')}")
    else:
        print(f"3. {t('Close_ai_agent')}")
    print(f"4. AI Agent Test Scrittura (Debug)")
    print(f"5. {t('menu_settings')}")
    print(f"6. {t('menu_exit')}")

    choice = input(f"{t('msg_prompt_choice')} ").strip()

    if choice == '1':
        logger.info("Navigating to Desktop Mode.")
        return "DESKTOP_MODE", selected_index
    elif choice == '2':
        logger.info("Navigating to Dual Audio.")
        return "DUAL_AUDIO", selected_index
    elif choice == '3':
        if not ai_agent.is_running():
            logger.info("Starting AI Agent in background.")
            ai_agent.start()
        else:
            logger.info("Closing AI Agent.")
            ai_agent.stop()
        return "MAIN_MENU", selected_index
    elif choice == '4':
        logger.info("Opening AI Agent testing console.")
        ai_agent.run_testing_console()
        return "MAIN_MENU", selected_index
    elif choice == '5':
        logger.info("Navigating to Settings.")
        return "SETTINGS", selected_index
    elif choice == '6':
        logger.info("Exiting application from main menu.")
        return "TURN_OFF", selected_index
    else:
        print(t('msg_invalid_choice'))
        logger.warning("Invalid menu choice entered: %s", choice)
        return "MAIN_MENU", selected_index