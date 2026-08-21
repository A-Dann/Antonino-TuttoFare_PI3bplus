#!/usr/bin/env python3
from menu_modules import desktop_mode, turn_off, dual_audio
import settings
from utils.i18n import t

def main():
    while True:
        print(f"\n--- {t('menu_title')} ---")
        print(f"1. {t('menu_desktop_mode')}")
        print(f"2. {t('menu_dual_audio')}")
        print(f"3. {t('menu_settings')}")
        print(f"4. {t('menu_exit')}")

        choice = input(f"{t('msg_prompt_choice')} ").strip()

        if choice == '1':
            desktop_mode.run()
        elif choice == '2':
            dual_audio.run()
        elif choice == '3':
            settings.run()
        elif choice == '4':
            turn_off.run()
            break
        else:
            print(t('msg_invalid_choice'))

if __name__ == "__main__":
    main()