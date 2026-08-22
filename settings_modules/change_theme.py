#!/usr/bin/env python3
"""
Change Theme Module.

Handles the rendering and user interaction for selecting and switching
theme components (palettes, styles, fonts) using horizontal selection controls.
"""

import pygame
from config import THEME_CONFIG_PATH
from graphic.menu_renderer import render_menu
from graphic.theme_manager import set_theme_component
from utils.file_utils import read_json
from utils.i18n import t

def draw_frame(virtual_screen, selected_index=0, events=None):
    """
    Renders a single frame of the multi-component theme configuration menu.
    """
    # 1. Definiamo le opzioni disponibili per ciascuna categoria
    palettes = ["default", "neon_cyberpunk"]
    styles = ["default", "neon_cyberpunk"]
    fonts = ["default"]

    # Leggiamo direttamente le preferenze salvate dal file di configurazione dei temi
    saved_prefs = read_json(THEME_CONFIG_PATH)
    current_palette = saved_prefs.get("palette", "default")
    current_style = saved_prefs.get("ui_style", "default")
    current_font = saved_prefs.get("font", "default")

    # 2. Struttura delle righe del menu
    rows = [
        {"category": "palettes", "label": "Palettes", "values": palettes, "current": current_palette},
        {"category": "styles", "label": "Styles", "values": styles, "current": current_style},
        {"category": "fonts", "label": "Fonts", "values": fonts, "current": current_font},
    ]
    
    back_label = t('settings_back_to_menu')
    
    menu_options = []
    for i, row in enumerate(rows):
        val_idx = row["values"].index(row["current"]) if row["current"] in row["values"] else 0
        val_name = row["values"][val_idx]
        
        if i == selected_index:
            menu_options.append(f"{row['label']}:  < {val_name} >")
        else:
            menu_options.append(f"{row['label']}:  {val_name}")

    menu_options.append(back_label)
    total_items = len(menu_options)

    if events is None:
        events = pygame.event.get()

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_index = (selected_index + 1) % total_items
            elif event.key == pygame.K_UP:
                selected_index = (selected_index - 1) % total_items
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                if selected_index < len(rows):
                    row = rows[selected_index]
                    val_list = row["values"]
                    current_val = row["current"]
                    
                    try:
                        curr_pos = val_list.index(current_val)
                    except ValueError:
                        curr_pos = 0
                    
                    if event.key == pygame.K_RIGHT:
                        new_pos = (curr_pos + 1) % len(val_list)
                    else:
                        new_pos = (curr_pos - 1) % len(val_list)
                        
                    new_val = val_list[new_pos]
                    
                    # Salva e applica immediatamente il componente modificato
                    set_theme_component(row["category"], new_val)
                    
            elif event.key == pygame.K_RETURN:
                if selected_index == total_items - 1:
                    return "SETTINGS", selected_index
            elif event.key == pygame.K_ESCAPE:
                return "SETTINGS", selected_index

    render_menu(
        screen=virtual_screen,
        menu_title="Configure Theme",
        menu_options=menu_options,
        selected_index=selected_index
    )

    return "CHANGE_THEME", selected_index