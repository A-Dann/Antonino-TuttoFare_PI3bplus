import json
from pathlib import Path

import pytest

from core.state_manager import DEFAULT_LANGUAGE
from core.translator import _flatten
from plugins.menu.main_menu import main_screen
from plugins.menu.settings_menu import settings_screen

LOCALES_DIR = Path(__file__).parents[1] / "locales"
LANGUAGES = sorted(file.stem for file in LOCALES_DIR.glob("*.json"))

# --- helpers ---------------------------------------------------------------

def load_texts(language):
    """The flat {key: text} dictionary of a language file."""
    data = json.loads((LOCALES_DIR / f"{language}.json").read_text(encoding="utf-8"))
    return _flatten(data)


# --- the language files ----------------------------------------------------

def test_the_default_language_has_a_file():
    assert DEFAULT_LANGUAGE in LANGUAGES


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_language_has_the_same_keys_as_the_default_language(language):
    default_keys = set(load_texts(DEFAULT_LANGUAGE))
    keys = set(load_texts(language))

    assert sorted(default_keys - keys) == []  # keys missing in this language
    assert sorted(keys - default_keys) == []  # keys that exist only in this language


@pytest.mark.parametrize("language", LANGUAGES)
def test_every_text_is_a_non_empty_string(language):
    texts = load_texts(language)

    empty = [key for key, text in texts.items() if not isinstance(text, str) or not text.strip()]

    assert empty == []


# --- the keys used by the screens ------------------------------------------

SCREENS = [main_screen, settings_screen]


def test_every_text_key_used_by_the_screens_exists_in_the_default_language():
    texts = load_texts(DEFAULT_LANGUAGE)
    used = {screen.title for screen in SCREENS}
    used |= {item.label for screen in SCREENS for item in screen.options}

    assert sorted(key for key in used if key not in texts) == []
