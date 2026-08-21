#!/usr/bin/env python3
"""
Sync Controller Module

This module acts as an intermediary layer between the settings interface 
and the synchronization logic (sync_engine).
"""

from utils.sync import sync_engine
from utils.i18n import t

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
        else:
            print(t('sync_time_and_place_failed'))
            
    except Exception as e:
        print(t('sync_time_and_place_critical_sync_error').format(e=e))
    
    # Wait for any key press before returning to the menu
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")
    return success

if __name__ == "__main__":
    run()