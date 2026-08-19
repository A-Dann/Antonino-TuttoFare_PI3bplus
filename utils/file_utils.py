#!/usr/bin/env python3
"""
General utility functions for file handling.
"""

import json
import os


def read_json(file_path: str) -> dict:
    """Safely read and parse a JSON file.

    Args:
        file_path (str): The absolute path to the JSON file.

    Returns:
        dict: The parsed dictionary, or an empty dictionary if it fails.
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_json(file_path: str, data: dict) -> bool:
    """Safely write data to a JSON file, creating directories if needed.

    Args:
        file_path (str): The absolute path to the JSON file.
        data (dict): The dictionary data to write.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False