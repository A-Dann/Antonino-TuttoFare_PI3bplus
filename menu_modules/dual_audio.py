#!/usr/bin/env python3
"""
Dual Audio Module
"""

from utils.i18n import t

def run():
    print(t('dual_audio_starting'))
    print(f"=== {t('dual_audio_title')} ===")
    print(t('dual_audio_dev'))
    input(t('msg_press_enter_return'))

if __name__ == "__main__":
    run()