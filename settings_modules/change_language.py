#!/usr/bin/env python3
"""
Change Language Module

This module allows the user to select and change the system language,
updating the configuration and reloading strings accordingly.
"""

import os
from utils.i18n import t, load_language, set_language, current_lang

def run():
    print(t('change_language_title'))

    languages = {
        "en": t('change_language_english'),
        "it": t('change_language_italian'),
        "es": t('change_language_spanish'),
    }

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n--- {t('change_language_settings')} ---")
        print(f"{t('key_current')}: {languages.get(current_lang, current_lang)}\n")

        codes = list(languages.keys())
        for idx, code in enumerate(codes, 1):
            print(f"{idx}. {languages[code]}")
        print(f"{len(codes) + 1}. {t('change_language_back_to_settings')}")

        choice = input(f"\n{t('_prompt_choice')} ").strip()

        if choice.isdigit():
            choice_idx = int(choice)
            if 1 <= choice_idx <= len(codes):
                selected_lang = codes[choice_idx - 1]
                set_language(selected_lang)
                print(f"\n{t('change_language_changed_succesfully')}")
                input(f"\n{t('msg_press_enter_return')}")
                break
            elif choice_idx == len(codes) + 1:
                break
        
        print(t('msg_invalid_choice'))

if __name__ == "__main__":
    run()