"""
Theme manager module for handling modular theme choices (palette, ui_style, font) 
and robust fallback mechanisms.
"""

import os
from config import THEME_CONFIG_PATH, THEMES_DIR_PATH
from utils.file_utils import read_json, write_json

# Default values for each modular component
DEFAULT_PALETTE = {
    "background": (30, 30, 30),
    "surface": (60, 60, 60),
    "surface_hover": (80, 80, 80),
    "border": (100, 100, 100),
    "text": (255, 255, 255),
    "shadow": (10, 10, 10, 150)
}

DEFAULT_UI_STYLE = {
    "button": {
        "height": 40,
        "width": 600,
        "border_radius": 8,
        "border_width": 2,
        "shadow_offset": 4,
        "margin_y": 15
    },
    "fonts": {
        "title_size": 35,
        "option_size": 25
    }
}

DEFAULT_FONT = {
    "font_name": None  # None uses Pygame's default font
}

current_theme = {}


def _get_component_file_path(category: str, name: str) -> str:
    """Build the absolute path for a specific theme component (palette, style, font)."""
    return os.path.join(THEMES_DIR_PATH, category, f"{name}.json")


def load_theme(palette_name: str = None, style_name: str = None, font_name: str = None) -> None:
    """
    Load and merge modular theme components with a chronological fallback chain:
    Requested -> Saved Preference -> Default.
    """
    global current_theme
        
    # Read user saved preferences safely via read_json (returns {} if file doesn't exist)
    saved_prefs = read_json(THEME_CONFIG_PATH)

    # If no preference or argument exists, default strictly to "default"
    target_palette = palette_name or saved_prefs.get("palette", "default")
    target_style = style_name or saved_prefs.get("ui_style", "default")
    target_font = font_name or saved_prefs.get("font", "default")

    # --- 1. Load Palette ---
    palette_file = _get_component_file_path("palettes", target_palette)
    loaded_palette = read_json(palette_file)
    if not loaded_palette and target_palette != "default":
        palette_file = _get_component_file_path("palettes", "default")
        loaded_palette = read_json(palette_file)

    final_palette = DEFAULT_PALETTE.copy()
    final_palette.update(loaded_palette)

    # --- 2. Load UI Style ---
    style_file = _get_component_file_path("styles", target_style)
    loaded_style = read_json(style_file)
    if not loaded_style and target_style != "default":
        style_file = _get_component_file_path("styles", "default")
        loaded_style = read_json(style_file)

    final_style = DEFAULT_UI_STYLE.copy()
    for key, value in loaded_style.items():
        if isinstance(value, dict) and key in final_style:
            final_style[key].update(value)
        else:
            final_style[key] = value

    # --- 3. Load Font ---
    font_file = _get_component_file_path("fonts", target_font)
    loaded_font = read_json(font_file)
    if not loaded_font and target_font != "default":
        font_file = _get_component_file_path("fonts", "default")
        loaded_font = read_json(font_file)

    final_font = DEFAULT_FONT.copy()
    final_font.update(loaded_font)

    # Combine everything into the final active theme structure expected by renderers
    current_theme = {
        "name": f"{target_palette}_{target_style}_{target_font}",
        "style": target_style,  # <--- AGGIUNGI QUESTA RIGA per esporre lo stile pulito
        "colors": final_palette,
        "button": final_style["button"],
        "fonts": {
            **final_style["fonts"],
            "font_name": final_font["font_name"]
        }
    }


def get_current_theme() -> dict:
    """Retrieve the currently active full theme dictionary."""
    if not current_theme:
        load_theme()
    return current_theme


def set_theme_component(category: str, name: str) -> None:
    """Update a single theme component (palette, ui_style, or font) and save preference."""
    
    saved_prefs = read_json(THEME_CONFIG_PATH)

    # Map category argument to config key names
    key_map = {
        "palettes": "palette",
        "styles": "ui_style",
        "fonts": "font"
    }
    
    config_key = key_map.get(category)
    if not config_key:
        return

    saved_prefs[config_key] = name
    
    # Reload full theme with updated settings
    load_theme(
        palette_name=saved_prefs.get("palette"),
        style_name=saved_prefs.get("ui_style"),
        font_name=saved_prefs.get("font")
    )
    
    write_json(THEME_CONFIG_PATH, saved_prefs)


# Initialize theme on module load using default configuration/saved state
load_theme()