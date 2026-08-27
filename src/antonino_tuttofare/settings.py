#!/usr/bin/env python3
"""
Settings Module (CLI State Version)

This module manages the settings menu adapted for the state machine architecture,
allowing users to view system info, configure Wi-Fi, synchronize time and place,
change the language, or return to the main menu via terminal inputs.
"""

import logging

from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run_cli_state(selected_index=0):
    """
    Renders the settings menu once in the terminal, processes a single choice input,
    and returns the next application state and selected index.
    """
    print(f"\n--- {t('settings_title')} ---")
    print(f"1. {t('settings_sys_info')}")
    print(f"2. {t('settings_configure_wifi')}")
    print(f"3. {t('settings_sync_time_place')}")
    print(f"4. {t('settings_change_lang')}")
    print(f"5. {t('settings_back_to_menu')}")

    choice = input(f"{t('msg_prompt_choice')} ").strip()

    if choice == '1':
        logger.info("Navigating to System Info.")
        return "SYSTEM_INFO", selected_index
    elif choice == '2':
        logger.info("Navigating to Wi-Fi Configuration.")
        return "WIFI_MENU", selected_index
    elif choice == '3':
        logger.info("Initiating time and place synchronization.")
        return "SYNC_TIME_AND_PLACE", selected_index
    elif choice == '4':
        logger.info("Navigating to Language Change.")
        return "CHANGE_LANGUAGE", selected_index
    elif choice == '5':
        print(t('msg_back_to_menu'))
        logger.info("Returning to Main Menu.")
        return "MAIN_MENU", selected_index
    else:
        print(t('msg_invalid_choice'))
        logger.warning("Invalid settings choice entered: %s", choice)
        return "SETTINGS", selected_index