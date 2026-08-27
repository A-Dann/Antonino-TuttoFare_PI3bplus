#!/usr/bin/env python3
"""
Turn Off / Shutdown Module

This module handles the graceful exit/shutdown process of the application, displaying
an ASCII art animation spelling out 'GOODBYE' letter by letter.
"""

import logging
import os
import time

from antonino_tuttofare.menu_modules import ai_agent
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

ascii_font = {
    'G': [
        " ######  ",
        " ##      ",
        " ##  ### ",
        " ##  ## ",
        "  ###### "
    ],
    'O': [
        "  ###### ",
        " ##  ## ",
        " ##  ## ",
        " ##  ## ",
        " ######  "
    ],
    'D': [
        " #####   ",
        " ##  ##  ",
        " ##   ## ",
        " ##  ##  ",
        " #####   "
    ],
    'B': [
        " #####   ",
        " ##  ##  ",
        " #####   ",
        " ##  ##  ",
        " #####   "
    ],
    'Y': [
        " ##   ## ",
        "  ## ##  ",
        "   ###   ",
        "    ##   ",
        "    ##   "
    ],
    'E': [
        " ####### ",
        " ##      ",
        " #####   ",
        " ##      ",
        " ####### "
    ]
}

def print_letter_by_letter(word, font):
    height = 5
    composite_lines = [""] * height
    
    for char in word:
        if char in font:
            letter_design = font[char]
            
            for i in range(height):
                composite_lines[i] += letter_design[i] + "  "
            
            os.system('clear' if os.name == 'posix' else 'cls')
            print("\n" * 2)
            for line in composite_lines:
                print(line)
            
            time.sleep(0.3)

def run():
    print(t('turn_off_system_exiting'))
    logger.info("Initiating application exit sequence...")

    if ai_agent.is_running():
            logger.info("Stopping AI Agent before shutting down...")
            ai_agent.stop()

    print_letter_by_letter("GOODBYE", ascii_font)

    print("\n" * 2)
    print(t('turn_off_shutting_down'), flush=True)
    logger.info("Shutdown sequence completed.")
    time.sleep(2)

if __name__ == "__main__":
    run()