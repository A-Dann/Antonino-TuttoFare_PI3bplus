#!/usr/bin/env python3
"""
Display management module for initializing the Pygame window 
and setting up the screen resolution for the Raspberry Multitool.
"""

import pygame
import socket

def init_display():
    """
    Initialize Pygame, set up the fixed 800x480 screen resolution,
    and configure the window caption using the system hostname.
    
    Returns:
        pygame.Surface: The main display surface object.
    """

    # Initialize all imported pygame modules
    pygame.init()
    screen = pygame.display.set_mode((800,480), pygame.FULLSCREEN)
    pygame.display.set_caption(f"{socket.gethostname()}")

    return screen