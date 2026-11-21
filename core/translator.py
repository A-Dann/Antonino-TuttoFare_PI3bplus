from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from core.state_keys import StateKeys
from core.state_manager import DEFAULT_LANGUAGE

if TYPE_CHECKING:
    from pathlib import Path

    from core.state_manager import StateManager

log = logging.getLogger(__name__)


def _flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    flatten_dict: dict[str, str] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flatten_dict.update(_flatten(value, prefix=prefix + key + "."))
        else:
            flatten_dict[prefix + key] = value

    return flatten_dict


class Translator:
    def __init__(self, state_manager: StateManager, locales_dir: Path) -> None:
        self._state_manager = state_manager
        self._translations: dict[str, dict[str, str]] = {}

        self._load(locales_dir)

    def _load(self, locales_dir: Path) -> None:
        for file in locales_dir.glob("*.json"):
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                log.warning("Cannot read the locale file %s", file)
                continue

            if not isinstance(data, dict):
                log.warning("Locale file: %s, does not have proper structure", file)
                continue

            self._translations[file.stem] = _flatten(data)

    def t(self, key: str, **params: Any) -> str:
        language = self._state_manager.get(StateKeys.LANGUAGE)

        text = None
        for candidate in (language, DEFAULT_LANGUAGE):
            text = self._translations.get(candidate, {}).get(key)
            if text is not None:
                break

        if text is None:
            log.warning("No translation for %s in %s", key, language)
            return key

        if params:
            try:
                text = text.format(**params)
            except (KeyError, IndexError, ValueError):
                log.warning("Couldn't format parameters for %s in %s", key, language)

        return text
