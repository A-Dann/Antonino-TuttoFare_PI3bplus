#!/usr/bin/env python3
"""
General utility functions for safe file and JSON handling.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Union


def read_json(file_path: Union[str, Path], default_value: Any = None) -> Any:
    """Safely read and parse a JSON file.

    Args:
        file_path (str | Path): The path to the JSON file.
        default_value (Any): Value to return if file doesn't exist or is corrupted.

    Returns:
        Any: The parsed data, or the default value (default: empty dict).
    """
    path = Path(file_path)
    fallback = default_value if default_value is not None else {}

    if not path.exists() or path.stat().st_size == 0:
        return fallback
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError, Exception):
        return fallback


def write_json(file_path: Union[str, Path], data: Dict[str, Any]) -> bool:
    """Safely write data to a JSON file using an atomic write pattern 
    to prevent data corruption during sudden power losses or crashes.

    Args:
        file_path (str | Path): The path to the JSON file.
        data (dict): The dictionary data to write.

    Returns:
        bool: True if successful, False otherwise.
    """
    path = Path(file_path)
    
    try:
        # Ensure target directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to a temporary file in the same directory first (atomic pattern)
        temp_path = path.with_suffix(path.suffix + ".tmp")
        
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            # Force physical write to storage (critical for Raspberry Pi SD cards)
            os.fsync(f.fileno())
            
        # Atomic replacement of the original file
        temp_path.replace(path)
        return True
        
    except (IOError, TypeError, Exception):
        # Cleanup temporary file if something went wrong
        if 'temp_path' in locals() and temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        return False