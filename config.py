import os

# Get the root directory of the project (one level above 'src', where 'data' is located)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path for the directories that contains useful data
DATA_DIR_PATH = os.path.join(PROJECT_ROOT, "data")
LOCALES_DIR_PATH = os.path.join(PROJECT_ROOT, "locales")

# Create the data directory if it does not exist
os.makedirs(DATA_DIR_PATH, exist_ok=True)

# Define absolute paths for the user configuration files
TIME_PLACE_JSON_CONFIG_PATH = os.path.join(DATA_DIR_PATH, "time&place_config.json")
LANGUAGE_CONFIG_PATH = os.path.join(DATA_DIR_PATH, "language_config.json")
TEMP_SELECTED_WIFI_INFO_JSON_PATH = os.path.join(DATA_DIR_PATH, "temp_selected_wifi_info.json")

DEFAULT_LANGUAGE = "en"  # Default language code

# Define absolute paths for scripts
CAPTIVE_PORTAL_SCRIPT_PATH = os.path.join(PROJECT_ROOT, "utils", "wifi", "wifi_captive_portal_engine.py")
