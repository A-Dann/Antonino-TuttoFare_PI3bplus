"""
Theme Drawers Module.
Contains pure visual drawing functions for UI styles, receiving fully scaled geometry and colors from the renderer.
"""

import pygame
from graphic.graphic_utils import handle_menu_viewport


def draw_default_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                      menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    """
    Default menu rendering style: top header bar and text options with gradient indicator lines.
    """
    bg_color = colors["background"]
    surface_color = colors["surface"]
    text_color = colors["text"]
    surface_hover_color = colors["surface_hover"]
    border_color = colors["border"]

    screen_width, _ = screen.get_size()
    center_x = screen_width // 2

    screen.fill(bg_color)

    # Render Title Header
    bar_height = int(50 * scale_factor)
    bar_rect = pygame.Rect(0, int(15 * scale_factor), screen_width, bar_height)
    pygame.draw.rect(screen, surface_color, bar_rect)
    
    border_width = max(1, int(button_config.get("border_width", 2) * scale_factor))
    pygame.draw.line(screen, border_color, (0, bar_rect.top), (screen_width, bar_rect.top), border_width)
    pygame.draw.line(screen, border_color, (0, bar_rect.bottom), (screen_width, bar_rect.bottom), border_width)

    title_surface = title_font.render(menu_title, True, text_color)
    title_rect = title_surface.get_rect(center=(center_x, bar_rect.centery))
    screen.blit(title_surface, title_rect)

    content_start_y = bar_rect.bottom + int(25 * scale_factor)
    current_y = content_start_y
    start_x = int(50 * scale_factor)
    item_spacing = int(50 * scale_factor)

    if menu_subtitle:
        subtitle_surf = option_font.render(menu_subtitle, True, (150, 150, 150))
        subtitle_rect = subtitle_surf.get_rect(topleft=(start_x, current_y))
        screen.blit(subtitle_surf, subtitle_rect)
        current_y += item_spacing

    # Utilizziamo la gestione universale anche sul default se necessario o gestiamo le righe
    for i, option_text in enumerate(menu_options):
        row_y = current_y + i * item_spacing
        is_hovered = (i == selected_index)

        current_text_color = surface_hover_color if is_hovered else text_color

        text_surf = option_font.render(option_text, True, current_text_color)
        text_rect = text_surf.get_rect(topleft=(start_x, row_y))
        screen.blit(text_surf, text_rect)

        if is_hovered:
            line_start_x = start_x
            line_end_x = int(screen_width * (4 / 6))
            line_y = text_rect.bottom + int(5 * scale_factor)

            line_width = line_end_x - line_start_x
            if line_width > 0:
                fade_surf = pygame.Surface((line_width, max(2, int(2 * scale_factor))), pygame.SRCALPHA)
                
                for x_offset in range(line_width):
                    alpha = int(255 * (1 - (x_offset / line_width)))
                    color_with_alpha = (*border_color[:3], alpha)
                    pygame.draw.line(fade_surf, color_with_alpha, (x_offset, 0), (x_offset, fade_surf.get_height() - 1))

                screen.blit(fade_surf, (line_start_x, line_y))


def draw_neon_cyberpunk_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                             menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    """
    Cyberpunk style: fixed header position, universal scrolling viewport, and fixed side arrows.
    """
    screen_width, _ = screen.get_size()
    center_x = screen_width // 2

    width = int(button_config.get("width", 500) * scale_factor)
    height = int(button_config.get("height", 45) * scale_factor)
    margin_y = int(button_config.get("margin_y", 12) * scale_factor)
    border_width = max(1, int(button_config.get("border_width", 3) * scale_factor))
    shadow_offset = int(button_config.get("shadow_offset", 5) * scale_factor)

    # 1. Sfondo
    screen.fill(colors.get("background", (30, 30, 30)))

    # 2. Header Fisso
    bar_height = int(50 * scale_factor)
    bar_rect = pygame.Rect(0, int(15 * scale_factor), screen_width, bar_height)
    pygame.draw.rect(screen, colors.get("surface", (60, 60, 60)), bar_rect)
    
    pygame.draw.line(screen, colors.get("border", (100, 100, 100)), (0, bar_rect.top), (screen_width, bar_rect.top), border_width)
    pygame.draw.line(screen, colors.get("border", (100, 100, 100)), (0, bar_rect.bottom), (screen_width, bar_rect.bottom), border_width)

    title_surf = title_font.render(menu_title, True, colors.get("text", (255, 255, 255)))
    title_rect = title_surf.get_rect(center=(center_x, bar_rect.centery))
    screen.blit(title_surf, title_rect)

    current_y = bar_rect.bottom + int(20 * scale_factor)
    start_x = int(50 * scale_factor)

    # 3. Sottotitolo (se presente)
    if menu_subtitle:
        subtitle_surf = option_font.render(menu_subtitle, True, (180, 180, 180))
        subtitle_rect = subtitle_surf.get_rect(topleft=(start_x, current_y))
        screen.blit(subtitle_surf, subtitle_rect)
        current_y += int(40 * scale_factor)

    # 4. CHIAMATA ALL'UTILITY UNIVERSALE DI VIEWPORT E FRECCE LATERALI
    start_index, end_index, visible_options = handle_menu_viewport(
        screen, menu_options, selected_index, current_y, height, margin_y, scale_factor
    )

    # 5. Disegno Bottoni visibili
    for idx, option_text in enumerate(visible_options):
        actual_index = start_index + idx
        btn_y = current_y + (idx * (height + margin_y))
        
        btn_rect = pygame.Rect(0, 0, width, height)
        btn_rect.center = (center_x, btn_y + height // 2)

        is_selected = (actual_index == selected_index)
        surface_color = colors.get("surface_hover" if is_selected else "surface", (60, 60, 60))
        border_color = colors.get("border", (100, 100, 100))

        # Ombra geometrica netta
        shadow_rect = btn_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect)
        
        # Box principale e bordo
        pygame.draw.rect(screen, surface_color, btn_rect)
        pygame.draw.rect(screen, border_color, btn_rect, width=border_width)

        # Testo centrato
        text_surf = option_font.render(option_text, True, colors.get("text", (255, 255, 255)))
        text_rect = text_surf.get_rect(center=btn_rect.center)
        screen.blit(text_surf, text_rect)


# DRAWER_CATALOG posizionato rigorosamente alla fine
DRAWER_CATALOG = {
    "default": draw_default_menu,
    "neon_cyberpunk": draw_neon_cyberpunk_menu,
}