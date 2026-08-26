#!/usr/bin/env python3
"""
Sync Controller Module

This module acts as an intermediary layer between the settings interface 
and the synchronization logic (sync_engine).
"""

import logging
from antonino_tuttofare.services import sync_engine
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run():
    """
    Function invoked by the settings interface to start the synchronization process.
    Executes the sync engine, displays the result, and waits for user input 
    before returning to the menu.
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
        success = False
    
    # Wait for user input before returning to the menu
    input(f"\n{t('msg_press_enter_to_continue')} ")
    return success

if __name__ == "__main__":
    run()