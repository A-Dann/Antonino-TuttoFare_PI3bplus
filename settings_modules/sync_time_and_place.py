#!/usr/bin/env python3
"""
Sync Controller Module

This module acts as an intermediary layer between the settings interface 
and the synchronization logic (sync_engine).
"""

from utils import sync_engine
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
            print(t('sync_completed_successfully'))
        else:
            print(t('sync_failed'))
            
    except Exception as e:
        print(t('critical_sync_error').format(e=e))
    
    # Wait for any key press before returning to the menu
    input(t('press_any_key_to_return'))
    return success

if __name__ == "__main__":
    run()