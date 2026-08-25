"""
Theme manager module for handling modular theme choices (palette, ui_style, font) 
and robust fallback mechanisms.
"""

import os
from config import THEME_CONFIG_PATH, THEMES_DIR_PATH
from utils.file_utils import read_json, write_json

# --- Default values based on generic semantic schema ---

# 1.DEFAULT_PALETTE: Mappatura semantica dei colori
DEFAULT_PALETTE = {
    "core": {
        "background_primary": (15, 15, 15),  # Sfondo scuro generale
        "background_secondary": (30, 30, 30),# Sfondo per pannelli/contenitori
        "background_tertiary": (45, 45, 45), # Sfondo per elementi terziari/overlay
        "border_color": (100, 100, 100)      # Colore standard dei bordi
    },
    "text": {
        "text_primary": (220, 220, 220),     # Testo principale/titoli
        "text_secondary": (180, 180, 180),   # Testo secondario/opzioni
        "text_disabled": (100, 100, 100),    # Testo disabilitato
        "text_inverted": (15, 15, 15)        # Testo su sfondo chiaro
    },
    "interactive": {
        "default": {
            "fill": (60, 60, 60),            # Sfondo bottone standard
            "text": (220, 220, 220),         # Testo bottone standard
            "border": (100, 100, 100)        # Bordo bottone standard
        },
        "hover": {
            "fill": (80, 80, 80),            # Sfondo bottone hover
            "text": (255, 255, 255),         # Testo bottone hover
            "border": (150, 150, 150)        # Bordo bottone hover
        },
        "selected": {
            "fill": (200, 200, 50),          # Sfondo bottone selezionato (Giallo default)
            "text": (15, 15, 15),            # Testo bottone selezionato
            "border": (220, 220, 100)        # Bordo bottone selezionato
        }
    }
}

# 2. DEFAULT_EFFECTS: Colori per effetti speciali (Glow, Glitch, Scanline)
DEFAULT_EFFECTS = {
    "highlight_primary": (50, 255, 50),      # Luce primaria (es. Verde fosforo)
    "highlight_secondary": (0, 100, 0),      # Luce secondaria (es. Verde scuro)
    "glitch_primary": (255, 0, 0),           # Glitch Canale R
    "glitch_secondary": (0, 0, 255),         # Glitch Canale B
    "overlay_effect": (0, 0, 0, 80)          # Colore per Scanline/Vignette (RGBA)
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


def _deep_update(target, source):
    """Recursively update a dictionary with another dictionary."""
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            _deep_update(target[key], value)
        else:
            target[key] = value
    return target


def _get_component_file_path(category: str, name: str) -> str:
    """Build the absolute path for a specific theme component (palette, style, font)."""
    return os.path.join(THEMES_DIR_PATH, category, f"{name}.json")


def load_theme(palette_name: str = None, style_name: str = None, font_name: str = None) -> None:
    """
    Load and merge modular theme components.
    Components are loaded independently based on preferences or arguments,
    falling back to 'default'.
    """
    global current_theme
        
    saved_prefs = read_json(THEME_CONFIG_PATH)

    target_palette = palette_name or saved_prefs.get("palette", "default")
    target_style = style_name or saved_prefs.get("ui_style", "default")
    target_font = font_name or saved_prefs.get("font", "default")

    # --- 1. Load Palette Data (I colori) ---
    palette_file = _get_component_file_path("palettes", target_palette)
    loaded_palette = read_json(palette_file)
    
    # Fallback su default per palette
    if not loaded_palette and target_palette != "default":
        palette_file = _get_component_file_path("palettes", "default")
        loaded_palette = read_json(palette_file)

    # Unisci con i default e la struttura semantica corretta
    final_palette_data = DEFAULT_PALETTE.copy()
    _deep_update(final_palette_data, loaded_palette)

    # Gestione effetti (possono essere nel file palette o default)
    final_effects_data = DEFAULT_EFFECTS.copy()
    if "effects" in loaded_palette and isinstance(loaded_palette["effects"], dict):
        _deep_update(final_effects_data, loaded_palette["effects"])

    # --- 2. Load UI Style Data (La logica di disegno) ---
    style_file = _get_component_file_path("styles", target_style)
    loaded_style = read_json(style_file)
    
    # Fallback su default per style
    if not loaded_style and target_style != "default":
        style_file = _get_component_file_path("styles", "default")
        loaded_style = read_json(style_file)

    final_style_data = DEFAULT_UI_STYLE.copy()
    _deep_update(final_style_data, loaded_style)

    # --- 3. Load Font Data (Il font) ---
    font_file = _get_component_file_path("fonts", target_font)
    loaded_font = read_json(font_file)
    
    if not loaded_font and target_font != "default":
        font_file = _get_component_file_path("fonts", "default")
        loaded_font = read_json(font_file)

    final_font_data = DEFAULT_FONT.copy()
    _deep_update(final_font_data, loaded_font)

    # --- 4. Combine into final active theme structure ---
    # Questo è il punto chiave: esponiamo i dati caricati *separatamente*
    # Sostituisci il blocco precedente con questo:
    current_theme = {
        "name": f"{target_palette}_{target_style}_{target_font}",
        "active_components": {
            "palette": target_palette,
            "ui_style": target_style,
            "font": target_font
        },
        "theme_data": {
            # Qui dentro ci sono i DATI puri, separati per categoria
            "colors": final_palette_data,
            "effects": final_effects_data,
            "layout_config": final_style_data, # Mappa i dati "style" come configurazione di layout
            "font_config": final_font_data
        },
        # --- Retrocompatibilità per i renderer che non sono ancora stati aggiornati ---
        # Se un renderer usa theme["colors"], glielo forniamo comunque,
        # ma ora è la struttura semantica corretta.
        "colors": final_palette_data, 
        "effects": final_effects_data,
        # Parametri specifici dei bottoni (mantenuti per compatibilità)
        "button": final_style_data.get("button", {}),
        # Parametri font (mantenuti per compatibilità)
        "fonts": {
            **final_style_data.get("fonts", {}),
            "font_name": final_font_data.get("font_name")
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