#!/usr/bin/env python3
"""
Change Language Module

This module allows the user to select and change the system language,
updating the configuration and reloading strings accordingly.
"""

import pygame
from graphic.menu_renderer import render_menu
from utils.i18n import t, set_language
import utils.i18n as i18n

def draw_frame(virtual_screen, selected_index=0, events=None):
    """
    Renders a single frame of the change language menu using passed events.
    """

    # 1. Define supported language codes
    codes = ["en", "it", "es"]

    # 2. Dictionary of supported languages with translated names
    languages = {
        "en": t('change_language_english'),
        "it": t('change_language_italian'),
        "es": t('change_language_spanish'),
    }

    # 3. Build the menu options list dynamically, including the back option
    current_lang_name = languages.get(i18n.current_lang, i18n.current_lang)
    language_options = [languages[code] for code in codes]
    language_options.append(t('change_language_back_to_settings'))

    # 4. Fallback event fetching if none are passed from the main loop
    if events is None:
        events = pygame.event.get()

    # 5. Process keyboard input events
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                # Move selection down (cyclic)
                selected_index = (selected_index + 1) % len(language_options)
            elif event.key == pygame.K_UP:
                # Move selection up (cyclic)
                selected_index = (selected_index - 1) % len(language_options)
            elif event.key == pygame.K_RETURN:
                # Handle selection confirmation on language or back option
                if 0 <= selected_index < len(codes):
                    selected_lang = codes[selected_index]
                    set_language(selected_lang)
                elif selected_index == len(codes):
                    return "SETTINGS", selected_index
            elif event.key == pygame.K_ESCAPE:
                # Quick return to settings using ESC
                return "SETTINGS", selected_index

    # 6. Render the current frame graphics with language title and subtitle
    render_menu(
        screen=virtual_screen,
        menu_title=f"{t('change_language_title')}",
        menu_subtitle=f"({t('key_current')}: {current_lang_name})",
        menu_options=language_options,
        selected_index=selected_index
    )

    # 7. Return the active state and current index back to the main loop
    return "CHANGE_LANGUAGE", selected_index