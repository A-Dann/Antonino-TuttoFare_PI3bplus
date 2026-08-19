import os

# Get the root directory of the project (one level above 'src', where 'data' is located)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path for the 'data' directory (same level as 'src')
DATA_DIR_PATH = os.path.join(PROJECT_ROOT, "data")

# Create the data directory if it does not exist
os.makedirs(DATA_DIR_PATH, exist_ok=True)

# Define absolute paths for the json configuration files
TIME_PLACE_JSON_CONFIG_PATH = os.path.join(DATA_DIR_PATH, "time&place_config.json")