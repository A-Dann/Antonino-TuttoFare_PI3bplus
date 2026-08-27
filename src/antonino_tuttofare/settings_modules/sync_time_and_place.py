#!/usr/bin/env python3
"""
Sync Controller Module (CLI State Version)

This module acts as an intermediary layer between the settings interface 
and the synchronization logic (sync_engine), adapted for the state machine architecture.
"""

import logging
from antonino_tuttofare.services import sync_engine
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run_cli_state(selected_index=0):
    """
    Executes the synchronization process, displays the result, waits for user input,
    and returns the SETTINGS state.
    """
    try:
        success = sync_engine.run_synchronization()
        
        if success:
            print(t('sync_time_and_place_completed_successfully'))
            logger.info("Time and place synchronized successfully.")
        else:
            print(t('sync_time_and_place_failed'))
            logger.warning("Time and place synchronization failed.")
            
    except Exception as e:
        error_msg = t('sync_time_and_place_critical_sync_error').format(e=e)
        print(error_msg)
        logger.exception("Critical synchronization error occurred: %s", e)
    
    input(f"\n{t('msg_press_enter_to_continue')} ")
    return "SETTINGS", selected_index