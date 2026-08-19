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

DEFAULT_LANGUAGE = "en"  # Default language code

# Path to the temporary pending Wi-Fi file
TEMP_WIFI_SSID_JSON_PATH = "/tmp/pending_wifi.json"