#!/usr/bin/env python3
"""
Internationalization (i18n) module for managing multi-language support.
"""

import os
import config
from utils.file_utils import read_json, write_json

current_lang = config.DEFAULT_LANGUAGE
translations = {}
fallback_translations = {}


def _get_locale_file_path(lang_code: str) -> str:
    """Build the absolute path for a given language code."""
    return os.path.join(config.LOCALES_DIR_PATH, f"{lang_code}.json")


def load_language(lang_code=None) -> None:
    """Load translation strings with a chronological fallback chain:
    Requested -> Previous/Saved -> Default.
    """
    global current_lang, translations, fallback_translations
    
    # 1. Determine the target language we want to load
    target_lang = lang_code
    previous_lang = current_lang  # Save the current language as "previous"

    # If no target language is provided, attempt to load the user's saved preference
    if not target_lang:
        if os.path.exists(config.LANGUAGE_CONFIG_PATH):
            user_data = read_json(config.LANGUAGE_CONFIG_PATH)
            target_lang = user_data.get("language", current_lang)
        else:
            target_lang = current_lang

    loaded_translations = {}

    # --- Attempt 1: Try to load the requested language ---
    lang_file = _get_locale_file_path(target_lang)
    loaded_translations = read_json(lang_file)

    # --- Attempt 2: If that fails, fall back to the previous language ---
    if not loaded_translations and target_lang != previous_lang:
        target_lang = previous_lang
        lang_file = _get_locale_file_path(target_lang)
        loaded_translations = read_json(lang_file)

    # --- Attempt 3: If that fails too, fall back to the default language ---
    if not loaded_translations and target_lang != config.DEFAULT_LANGUAGE:
        target_lang = config.DEFAULT_LANGUAGE
        lang_file = _get_locale_file_path(target_lang)
        loaded_translations = read_json(lang_file)

    # Always load the default language as a granular fallback for missing individual words
    default_lang_file = _get_locale_file_path(config.DEFAULT_LANGUAGE)
    fallback_translations = read_json(default_lang_file)

    current_lang = target_lang
    translations = loaded_translations


def t(key: str) -> str:
    """Retrieve the translated string for a given key, searching recursively."""
    if not translations and not fallback_translations:
        load_language()
    
    def find_key(data, target_key):
        if not isinstance(data, dict):
            return None
        if target_key in data:
            return data[target_key]
        for v in data.values():
            if isinstance(v, dict):
                res = find_key(v, target_key)
                if res is not None:
                    return res
        return None

    result = find_key(translations, key)
    if result is not None:
        return result
    
    result = find_key(fallback_translations, key)
    if result is not None:
        return result
    
    return key


def set_language(lang_code: str) -> None:
    """Set a new language and save preference to disk if it differs from current."""
    global current_lang
    
    # If the requested language is already the active one, do nothing
    if lang_code == current_lang:
        return

    lang_file = _get_locale_file_path(lang_code)
    test_data = read_json(lang_file)
    
    if not test_data:
        return

    current_lang = lang_code
    write_json(config.LANGUAGE_CONFIG_PATH, {"language": lang_code})
    load_language(lang_code)


load_language()