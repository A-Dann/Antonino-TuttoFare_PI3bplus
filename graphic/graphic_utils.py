"""
Graphic Utilities Module.
Handles resolution scaling factors and common helper functions for rendering.
"""

import pygame

def get_scale_factor(screen: pygame.Surface) -> float:
    """
    Calculate the dynamic scale factor based on the current screen height 
    relative to the base reference resolution (480px).
    """
    _, screen_height = screen.get_size()
    return screen_height / 480.0

def scale_value(value: int, scale_factor: float) -> int:
    """Helper to scale an integer dimension cleanly."""
    return int(value * scale_factor)

def handle_menu_viewport(screen: pygame.Surface, menu_options: list, selected_index: int, 
                           start_y: int, item_height: int, margin_y: int, scale_factor: float) -> tuple:
    """
    Gestisce universalmente lo scrolling delle opzioni e disegna le due frecce fisse 
    sul lato destro (semitrasparenti se non c'è altro spazio in quella direzione).
    """
    screen_width, screen_height = screen.get_size()
    item_total_height = item_height + margin_y
    
    # Spazio verticale disponibile per le opzioni
    available_height = screen_height - start_y - int(30 * scale_factor)
    max_visible_items = max(1, available_height // item_total_height)

    # Se ci stanno tutti, restituisce tutto senza frecce
    if len(menu_options) <= max_visible_items:
        return 0, len(menu_options), menu_options

    # Calcolo della finestra basata sull'elemento selezionato
    start_index = max(0, min(selected_index - max_visible_items // 2, len(menu_options) - max_visible_items))
    end_index = min(start_index + max_visible_items, len(menu_options))
    visible_options = menu_options[start_index:end_index]

    # --- Disegno frecce fisse sul lato destro ---
    arrow_x = screen_width - int(40 * scale_factor)
    arrow_font = pygame.font.Font(None, int(32 * scale_factor))

    # Freccia SU fissa in alto nell'area dei contenuti
    can_scroll_up = start_index > 0
    alpha_up = 255 if can_scroll_up else 50  # Semitrasparente se non disponibile
    
    arrow_up_surf = arrow_font.render("▲", True, (255, 255, 255))
    arrow_up_surf.set_alpha(alpha_up)
    arrow_up_rect = arrow_up_surf.get_rect(center=(arrow_x, start_y + int(10 * scale_factor)))
    screen.blit(arrow_up_surf, arrow_up_rect)

    # Freccia GIÙ fissa in basso nell'area dei contenuti
    can_scroll_down = end_index < len(menu_options)
    alpha_down = 255 if can_scroll_down else 50  # Semitrasparente se non disponibile

    arrow_down_surf = arrow_font.render("▼", True, (255, 255, 255))
    arrow_down_surf.set_alpha(alpha_down)
    
    last_item_bottom = start_y + (len(visible_options) * item_total_height)
    arrow_down_rect = arrow_down_surf.get_rect(center=(arrow_x, last_item_bottom - int(margin_y // 2)))
    screen.blit(arrow_down_surf, arrow_down_rect)

    return start_index, end_index, visible_options

def flatten_palette(palette: dict) -> dict:
    """Converte una palette annidata (core, text, interactive) in un dizionario piatto."""
    flat = {}
    if not isinstance(palette, dict):
        return flat

    for section_name, section_value in palette.items():
        if isinstance(section_value, dict):
            for k, v in section_value.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        if isinstance(sub_v, (tuple, list)):
                            flat[f"{k}_{sub_k}"] = sub_v
                elif isinstance(v, (tuple, list)):
                    flat[k] = v
        elif isinstance(section_value, (tuple, list)):
            flat[section_name] = section_value

    if "interactive" in palette and isinstance(palette["interactive"], dict):
        inter = palette["interactive"]
        if "default" in inter and isinstance(inter["default"], dict):
            if "fill" in inter["default"]:
                flat["fill"] = inter["default"]["fill"]
                flat["default_fill"] = inter["default"]["fill"]
        if "selected" in inter and isinstance(inter["selected"], dict):
            if "fill" in inter["selected"]:
                flat["hover_fill"] = inter["selected"]["fill"]
                flat["selected_fill"] = inter["selected"]["fill"]

    return flat