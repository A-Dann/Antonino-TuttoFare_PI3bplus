#!/usr/bin/env python3
"""
Change Language Module (CLI State Version)

This module allows the user to select and change the system language adapted
for the state machine architecture, updating the configuration and reloading strings.
"""

import os

from antonino_tuttofare.utility.i18n import t, set_language, current_lang
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)

def run_cli_state(selected_index=0):
    """
    Renders the language selection menu once in the terminal, processes a single choice input,
    and returns the next application state and selected index.
    """
    logger.debug("Rendering language selection CLI menu state...")

    languages = {
        "en": t('change_language_english'),
        "it": t('change_language_italian'),
        "es": t('change_language_spanish'),
    }

    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"\n--- {t('change_language_settings')} ---")
    print(f"{t('key_current')}: {languages.get(current_lang, current_lang)}\n")

    codes = list(languages.keys())
    for idx, code in enumerate(codes, 1):
        print(f"{idx}. {languages[code]}")
    print(f"{len(codes) + 1}. {t('change_language_back_to_settings')}")

    choice = input(f"\n{t('msg_prompt_choice')} ").strip()

    if choice.isdigit():
        choice_idx = int(choice)
        if 1 <= choice_idx <= len(codes):
            selected_lang = codes[choice_idx - 1]
            set_language(selected_lang)
            logger.info(f"System language successfully changed to: {selected_lang}")
            print(f"\n{t('change_language_changed_succesfully')}")
            input(f"\n{t('msg_press_enter_return')} ")
            return "CHANGE_LANGUAGE", selected_index
        elif choice_idx == len(codes) + 1:
            logger.debug("User exited language settings menu.")
            return "SETTINGS", selected_index

    print(t('msg_invalid_choice'))
    logger.debug(f"User entered invalid language selection choice: '{choice}'")
    input(f"\n{t('msg_press_enter_to_continue')} ")
    return "CHANGE_LANGUAGE", selected_index