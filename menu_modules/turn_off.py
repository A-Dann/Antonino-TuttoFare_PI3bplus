import subprocess
import time
import os
from utils.i18n import t

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
            
            os.system('clear')
            print("\n" * 2)
            for line in composite_lines:
                print(line)
            
            time.sleep(0.3)

def run():
    print(t('msg_exit'))

    print_letter_by_letter("GOODBYE", ascii_font)

    print("\n" * 2)
    print(t('msg_shutting_down'), flush=True)
    time.sleep(2)

    subprocess.run(["sudo", "shutdown", "now"])