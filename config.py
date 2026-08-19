import os

# Get the absolute path of the 'src' directory where this configuration file is located
SRC_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# Get the root directory of the project (one level above 'src', where 'data' is located)
PROJECT_ROOT = os.path.dirname(SRC_DIR_PATH)

# Define the absolute path for the 'data' directory (same level as 'src')
DATA_DIR_PATH = os.path.join(PROJECT_ROOT, "data")

# Create the data directory if it does not exist
os.makedirs(DATA_DIR_PATH, exist_ok=True)

# Define absolute paths for the settings menu
SETTINGS_PATH = os.path.join(SRC_DIR_PATH, "settings.py")

# Define absolute paths for the modules located in the main menu
DESKTOP_MODE_PATH = os.path.join(SRC_DIR_PATH, "menu_modules", "desktop_mode.py")
DUAL_AUDIO_PATH = os.path.join(SRC_DIR_PATH, "menu_modules", "dual_audio.py")
TURN_OFF_PATH = os.path.join(SRC_DIR_PATH, "menu_modules", "turn_off.py")

# Define absolute paths for the modules located in the setting menu
SYNC_TIME_PLACE_PATH = os.path.join(SRC_DIR_PATH, "settings_modules", "sync_time_and_place.py")
SYSTEM_INFO_PATH = os.path.join(SRC_DIR_PATH, "settings_modules", "system_info.py")

# Define absolute paths for the json configuration files
TIME_PLACE_JSON_CONFIG_PATH = os.path.join(DATA_DIR_PATH, "time&place_config.json")