"""
Menu Renderer Module.
Handles the graphical rendering of all menus.
"""

import pygame
from graphic.theme_manager import get_current_theme

def render_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int = -1) -> None:
    """
    Renders the menu screen with a title and a list of interactive options.
    Applies colors, fonts, shadows, and borders defined in the global theme.

    Args:
        screen (pygame.Surface): The main display surface.
        menu_title (str): The title text to display at the top.
        menu_options (list): A list of strings representing the menu choices.
        selected_index (int): Index of the currently hovered/selected option.
    """
    # 1. Retrieve the active global theme
    theme = get_current_theme()
    
    colors = theme["colors"]
    button_style = theme["button"]
    fonts_style = theme["fonts"]

    # 2. Extract base colors
    bg_color = colors["background"]
    surface_color = colors["surface"]
    surface_hover_color = colors["surface_hover"]
    border_color = colors["border"]
    text_color = colors["text"]
    shadow_color = colors["shadow"]

    # 3. Extract button dimensions and text sizes from UI style
    btn_width = button_style["width"]
    btn_height = button_style["height"]
    border_radius = button_style["border_radius"]
    border_width = button_style["border_width"]
    shadow_offset = button_style["shadow_offset"]
    margin_y = button_style["margin_y"]
    
    # 4. Extract font configurations (sizes belong here according to DEFAULT_UI_STYLE)
    title_size = fonts_style["title_size"]
    option_size = fonts_style["option_size"]
    
    # 5. Extract font family name
    font_name = fonts_style["font_name"]

    # Initialize Pygame fonts
    title_font = pygame.font.SysFont(font_name, title_size)
    option_font = pygame.font.SysFont(font_name, option_size)

    # Clear the screen with background color
    screen.fill(bg_color)

    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    # 5. Render the title header with a full-width background bar and open side borders
    title_surface = title_font.render(menu_title, True, text_color)
    title_rect = title_surface.get_rect(center=(center_x, 80))

    bar_height = title_rect.height + 25
    bar_rect = pygame.Rect(0, 45, screen_width, bar_height)

    # Draw the full-width title background bar
    pygame.draw.rect(screen, surface_color, bar_rect)
    
    # Draw horizontal top and bottom border lines (leaving sides open)
    if border_width > 0:
        pygame.draw.line(screen, border_color, (0, bar_rect.top), (screen_width, bar_rect.top), border_width)
        pygame.draw.line(screen, border_color, (0, bar_rect.bottom), (screen_width, bar_rect.bottom), border_width)

    # Blit the title text over the bar
    screen.blit(title_surface, title_rect)

    # 6. Calculate starting position to center buttons vertically
    total_buttons_height = len(menu_options) * btn_height + (len(menu_options) - 1) * margin_y
    start_y = (screen_height - total_buttons_height) // 2 + 50

    # 7. Render menu options as modular buttons
    for i, option_text in enumerate(menu_options):
        current_y = start_y + i * (btn_height + margin_y)
        
        # Button rectangle
        btn_rect = pygame.Rect(0, 0, btn_width, btn_height)
        btn_rect.center = (center_x, current_y)

        # Select surface color (hover or normal)
        is_hovered = (i == selected_index)
        current_surface_color = surface_hover_color if is_hovered else surface_color

        # Draw button shadow (if defined)
        if shadow_offset > 0:
            shadow_rect = btn_rect.copy()
            shadow_rect.x += shadow_offset
            shadow_rect.y += shadow_offset
            
            # Create transparent surface for shadow
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=border_radius)
            screen.blit(shadow_surf, shadow_rect.topleft)

        # Draw button body
        pygame.draw.rect(screen, current_surface_color, btn_rect, border_radius=border_radius)
        
        # Draw button border
        if border_width > 0:
            pygame.draw.rect(screen, border_color, btn_rect, width=border_width, border_radius=border_radius)

        # Render centered text
        text_surf = option_font.render(option_text, True, text_color)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        screen.blit(text_surf, text_rect)