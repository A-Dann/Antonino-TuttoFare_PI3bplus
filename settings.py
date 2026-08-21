#!/usr/bin/env python3

import settings_modules.system_info as system_info
import settings_modules.configure_wifi as configure_wifi
import settings_modules.sync_time_and_place as sync_time_and_place
import settings_modules.change_language as change_language
from utils.i18n import t

def run():
    print(t('settings_starting'))

    while True:
        print(f"\n--- {t('settings_title')} ---")
        print(f"1. {t('settings_sys_info')}")
        print(f"2. {t('settings_configure_wifi')}")
        print(f"3. {t('settings_sync_time_place')}")
        print(f"4. {t('settings_change_lang')}")
        print(f"5. {t('settings_back_to_menu')}")

        choice = input(f"{t('msg_prompt_choice')} ").strip()

        if choice == '1':
            system_info.run()
        elif choice == '2':
            configure_wifi.run()
        elif choice == '3':
            sync_time_and_place.run()
        elif choice == '4':
            change_language.run()
        elif choice == '5':
            print(t('msg_back_to_menu'))
            return
        else:
            print(t('msg_invalid_choice'))