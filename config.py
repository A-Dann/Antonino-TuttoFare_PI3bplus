import os

# Get the absolute path of the directory where this configuration file is located
BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# Define absolute paths for the various scripts called by the main menu
DESKTOP_MODE_PATH = os.path.join(BASE_DIR_PATH, "desktop_mode.py")
DUAL_AUDIO_PATH = os.path.join(BASE_DIR_PATH, "dual_audio.py")
TURN_OFF_PATH = os.path.join(BASE_DIR_PATH, "turn_off.py")

# Define absolute paths for the json configuration files
TIME_PLACE_JSON_CONFIG_PATH = os.path.join(BASE_DIR_PATH, "time&place_config.json")