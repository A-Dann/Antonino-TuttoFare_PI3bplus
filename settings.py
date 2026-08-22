#!/usr/bin/env python3
"""
Settings Menu Module (Pygame UI Version)
"""

import pygame
from graphic.menu_renderer import render_menu
from utils.i18n import t


def draw_frame(virtual_screen, selected_index=0, events=None):
    """
    Renders a single frame of the settings menu using passed events.
    """

    # 1. Define translated options for the settings submenu
    settings_options = [
        t('settings_sys_info'),
        t('settings_configure_wifi'),
        t('settings_sync_time_place'),
        t('settings_change_theme'),
        t('settings_change_lang'),
        t('settings_back_to_menu')
    ]

    # 2. Fallback event fetching if none are passed from the main loop
    if events is None:
        events = pygame.event.get()

    # 3. Process keyboard input events
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                # Move selection down (cyclic)
                selected_index = (selected_index + 1) % len(settings_options)
            elif event.key == pygame.K_UP:
                # Move selection up (cyclic)
                selected_index = (selected_index - 1) % len(settings_options)
            elif event.key == pygame.K_RETURN:
                # Handle selection confirmation on options
                if selected_index == 1:
                    return "CONFIGURE_WIFI", selected_index
                elif selected_index == 3:
                    return "CHANGE_THEME", selected_index
                elif selected_index == 4:
                    return "CHANGE_LANGUAGE", selected_index
                elif selected_index == 5:
                    return "MAIN_MENU", selected_index
                # Quick return to the main menu using ESC
            elif event.key == pygame.K_ESCAPE:
                return "MAIN_MENU", selected_index

    # 4. Render the current frame graphics
    render_menu(
        screen=virtual_screen,
        menu_title=t('settings_title'),
        menu_options=settings_options,
        selected_index=selected_index
    )

    # 5. Return the active state and current index back to the main loop
    return "SETTINGS", selected_index