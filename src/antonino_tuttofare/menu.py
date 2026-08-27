#!/usr/bin/env python3
"""
Main Menu Module

This module serves as the primary entry point and main menu loop of the application,
allowing users to navigate between desktop mode, dual audio, settings, and exit.
"""

import logging

from antonino_tuttofare.menu_modules import desktop_mode, dual_audio, ai_agent, turn_off
from antonino_tuttofare import settings
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def main():
    logger.info("Main menu started.")
    while True:
        print(f"\n--- {t('menu_title')} ---")
        print(f"1. {t('menu_desktop_mode')}")
        print(f"2. {t('menu_dual_audio')}")
        print(f"3. {t('ai_agent')}")
        print(f"4. {t('menu_settings')}")
        print(f"5. {t('menu_exit')}")

        choice = input(f"{t('msg_prompt_choice')} ").strip()

        if choice == '1':
            logger.info("Navigating to Desktop Mode.")
            desktop_mode.run()
        elif choice == '2':
            logger.info("Navigating to Dual Audio.")
            dual_audio.run()
        elif choice == '3':
            logger.info("Navigating to Dual Audio.")
            ai_agent.run()
        elif choice == '4':
            logger.info("Navigating to Settings.")
            settings.run()
        elif choice == '5':
            logger.info("Exiting application from main menu.")
            turn_off.run()
            break
        else:
            print(t('msg_invalid_choice'))
            logger.warning("Invalid menu choice entered: %s", choice)

if __name__ == "__main__":
    main()