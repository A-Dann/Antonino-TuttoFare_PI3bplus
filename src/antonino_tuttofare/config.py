import os
from pathlib import Path

# Project root and static assets/source paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CODE_ROOT_PATH = PROJECT_ROOT / "src" / "antonino_tuttofare"
ASSETS_DIR_PATH = PROJECT_ROOT / "assets"
LOCALES_DIR_PATH = ASSETS_DIR_PATH / "locales"
WAKEWORD_DIR_PATH = ASSETS_DIR_PATH / "wakewords"
TEMPLATES_DIR_PATH = ASSETS_DIR_PATH / "templates"
STATIC_DIR_PATH = ASSETS_DIR_PATH / "static"

# Application name used for system directories
APP_NAME = "antonino_tuttofare"

# --- 1. CONFIGURATION (Persistent user preferences) ---
# Standard: ~/.config/antonino_tuttofare/ (survives code updates)
CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME

# --- 2. DATA (Persistent application state, databases, etc.) ---
# Standard: ~/.local/share/antonino_tuttofare/
DATA_DIR = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME

# --- 3. TEMPORARY (Transient files, cache, RAM) ---
# Standard: /tmp/antonino_tuttofare/ (automatically cleared by the system)
TEMP_DIR = Path(os.getenv("XDG_RUNTIME_DIR", "/tmp")) / APP_NAME

# Automatically create all required directories if they don't exist on the system
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Configuration file paths (stored in .config)
LANGUAGE_CONFIG_PATH = CONFIG_DIR / "language_config.json"

# Persistent application state / dynamic data paths (stored in .local/share)
TIME_PLACE_JSON_CONFIG_PATH = DATA_DIR / "time&place_config.json"

# Temporary file paths (stored in /tmp)
TEMP_SELECTED_WIFI_INFO_JSON_PATH = TEMP_DIR / "temp_selected_wifi_info.json"


DEFAULT_LANGUAGE = "en"  # Default language code

# Internal script paths
CAPTIVE_PORTAL_SCRIPT_PATH = CODE_ROOT_PATH / "services" / "wifi_captive_portal_engine.py"