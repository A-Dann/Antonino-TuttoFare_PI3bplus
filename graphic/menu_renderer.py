"""
Menu Renderer Module.
Handles the graphical rendering of all menus using central graphic utilities and theme drawers.
"""

import pygame
from graphic.theme_manager import get_current_theme
from graphic.graphic_utils import get_scale_factor
from graphic.theme_drawer import DRAWER_CATALOG

from graphic.graphic_utils import get_scale_factor, flatten_palette
from graphic.theme_manager import get_current_theme
from graphic.theme_drawer import DRAWER_CATALOG

def render_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int = -1, menu_subtitle: str = None) -> None:
    theme = get_current_theme()
    
    active_comp = theme.get("active_components", {})
    style_name = active_comp.get("ui_style", theme.get("style", theme.get("name", "default")))
    
    drawer_func = DRAWER_CATALOG.get(style_name, DRAWER_CATALOG.get("default"))

    # Appiattiamo la palette complessa in un dizionario con chiavi lineari
    colors = flatten_palette(theme.get("colors", {}))
    
    fonts_style = theme["fonts"]
    button_config = theme.get("button", {})

    scale_factor = get_scale_factor(screen)

    title_size = int(fonts_style["title_size"] * scale_factor)
    option_size = int(fonts_style["option_size"] * scale_factor)
    font_name = fonts_style["font_name"]

    try:
        title_font = pygame.font.SysFont(font_name, title_size)
        option_font = pygame.font.SysFont(font_name, option_size)
    except Exception:
        title_font = pygame.font.Font(None, title_size)
        option_font = pygame.font.Font(None, option_size)

    if callable(drawer_func):
        drawer_func(
            screen=screen,
            menu_title=menu_title,
            menu_options=menu_options,
            selected_index=selected_index,
            menu_subtitle=menu_subtitle,
            title_font=title_font,
            option_font=option_font,
            colors=colors, # Ora riceve colori piatti e leggibili
            button_config=button_config,
            scale_factor=scale_factor
        )
    else:
        raise TypeError(f"Drawer function for style '{style_name}' is not callable.")