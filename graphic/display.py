#!/usr/bin/env python3
"""
Display management module for initializing the Pygame window 
at native resolution for crystal-clear text rendering.
"""

import pygame
import socket

def init_display():
    """
    Initialize Pygame and set up a native resolution window 
    so that fonts render crisp and clear directly on physical pixels.
    """
    pygame.init()

    display_info = pygame.display.Info()
    native_width = display_info.current_w
    native_height = display_info.current_h

    # Finestra a risoluzione nativa reale del monitor
    screen = pygame.display.set_mode((native_width, native_height), pygame.FULLSCREEN)
    pygame.display.set_caption(f"{socket.gethostname()}")

    return screen, screen

def update_display(screen, virtual_screen):
    """
    Direct display refresh.
    """
    pygame.display.flip()