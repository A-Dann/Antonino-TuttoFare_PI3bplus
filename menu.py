#!/usr/bin/env python3
"""
Main Menu Module (Pygame UI Version)
"""

import pygame
from graphic.menu_renderer import render_menu
from menu_modules import desktop_mode, turn_off, dual_audio
from utils.i18n import t

def draw_frame(virtual_screen, selected_index=0, events=None):
    """
    Renders a single frame of the main menu using passed events.
    """
    
    # 1. Define translated options for the main menu
    menu_options = [
        t('menu_desktop_mode'),
        t('menu_dual_audio'),
        t('menu_settings'),
        t('menu_exit')
    ]

    # 2. Fallback event fetching if none are passed from the main loop
    if events is None:
        events = pygame.event.get()

    # 3. Process keyboard input events
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                # Move selection down (cyclic)
                selected_index = (selected_index + 1) % len(menu_options)
            elif event.key == pygame.K_UP:
                # Move selection up (cyclic)
                selected_index = (selected_index - 1) % len(menu_options)
            elif event.key == pygame.K_RETURN:
                # Handle selection confirmation on options
                if selected_index == 0:
                    desktop_mode.run()
                elif selected_index == 1:
                    dual_audio.run()
                elif selected_index == 2:
                    return "SETTINGS", selected_index
                elif selected_index == 3:
                    turn_off.run()
                    return "EXIT", selected_index
            elif event.key == pygame.K_ESCAPE:
                # Quick exit using ESC
                turn_off.run()
                return "EXIT", selected_index

    # 4. Render the current frame graphics
    render_menu(
        screen=virtual_screen,
        menu_title=t('menu_title'),
        menu_options=menu_options,
        selected_index=selected_index
    )

    # 5. Return the active state and current index back to the main loop
    return "MAIN_MENU", selected_index