#!/usr/bin/env python3
"""
Settings Module

This module manages the settings menu, allowing the user to view system info,
configure Wi-Fi, synchronize time and place, change the language, or return to the main menu.
"""

import logging

from antonino_tuttofare.settings_modules import (
    system_info,
    wifi_menu,
    sync_time_and_place,
    change_language,
)
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run():
    print(t('settings_starting'))
    logger.info("Settings menu opened.")

    while True:
        print(f"\n--- {t('settings_title')} ---")
        print(f"1. {t('settings_sys_info')}")
        print(f"2. {t('settings_configure_wifi')}")
        print(f"3. {t('settings_sync_time_place')}")
        print(f"4. {t('settings_change_lang')}")
        print(f"5. {t('settings_back_to_menu')}")

        choice = input(f"{t('msg_prompt_choice')} ").strip()

        if choice == '1':
            logger.info("Navigating to System Info.")
            system_info.run()
        elif choice == '2':
            logger.info("Navigating to Wi-Fi Configuration.")
            wifi_menu.run()
        elif choice == '3':
            logger.info("Initiating time and place synchronization.")
            sync_time_and_place.run()
        elif choice == '4':
            logger.info("Navigating to Language Change.")
            change_language.run()
        elif choice == '5':
            print(t('msg_back_to_menu'))
            logger.info("Returning to Main Menu.")
            return
        else:
            print(t('msg_invalid_choice'))
            logger.warning("Invalid settings choice entered: %s", choice)

if __name__ == "__main__":
    run()