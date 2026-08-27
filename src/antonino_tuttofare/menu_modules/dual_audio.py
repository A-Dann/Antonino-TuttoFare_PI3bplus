#!/usr/bin/env python3
"""
Dual Audio Module (CLI State Version)

This module handles the dual audio configuration adapted for the state machine architecture.
"""

import logging
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run_cli_state(selected_index=0):
    """
    Renders the dual audio menu/information screen once, waits for user input,
    and returns the main menu state.
    """
    logger.info("Running Dual Audio state...")
    
    print(t('dual_audio_starting'))
    print(f"=== {t('dual_audio_title')} ===")
    print(t('dual_audio_dev'))
    
    print("\n-------------------------")
    input(f"{t('msg_press_enter_return')} ")
    
    logger.info("Exiting dual audio menu.")
    return "MAIN_MENU", selected_index