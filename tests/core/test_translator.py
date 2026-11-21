import json
import logging

from core.event_bus import EventBus
from core.state_keys import StateKeys
from core.state_manager import StateManager
from core.translator import Translator, _flatten

# --- helpers ---------------------------------------------------------------

def write_locale(directory, language, messages):
    (directory / f"{language}.json").write_text(json.dumps(messages), encoding="utf-8")


def make_translator(directory, locales):
    """Write one file per language in `directory`, then build a Translator on it.

    `locales` is {"en": {...}, "it": {...}}. Return (translator, state_manager):
    the test changes the language through the state manager.
    """
    for language, messages in locales.items():
        write_locale(directory, language, messages)
    state_manager = StateManager(EventBus())
    return Translator(state_manager, directory), state_manager


HELLO = {"en": {"hello": "Hello"}, "it": {"hello": "Ciao"}}

# --- _flatten --------------------------------------------------------------

def test_flatten_of_an_empty_dict_is_empty():
    assert _flatten({}) == {}


def test_flatten_keeps_a_flat_dict_unchanged():
    assert _flatten({"a": "1"}) == {"a": "1"}


def test_flatten_joins_the_keys_of_a_nested_dict_with_a_dot():
    assert _flatten({"a": {"x": "1"}}) == {"a.x": "1"}


def test_flatten_joins_the_keys_of_two_nested_levels():
    assert _flatten({"a": {"b": {"c": "1"}}}) == {"a.b.c": "1"}


def test_flatten_keeps_the_keys_that_come_before_a_nested_group():
    assert _flatten({"a": "1", "b": {"x": "2"}}) == {"a": "1", "b.x": "2"}


def test_flatten_adds_the_given_prefix_to_every_key():
    assert _flatten({"x": "1", "y": "2"}, "a.") == {"a.x": "1", "a.y": "2"}


# --- t: the language -------------------------------------------------------

def test_t_uses_english_when_the_language_was_never_changed(tmp_path):
    translator, _ = make_translator(tmp_path, HELLO)

    assert translator.t("hello") == "Hello"


def test_t_follows_the_language_in_the_state(tmp_path):
    translator, state_manager = make_translator(tmp_path, HELLO)

    state_manager.set(StateKeys.LANGUAGE, "it")

    assert translator.t("hello") == "Ciao"


def test_t_reads_a_nested_key_with_dots(tmp_path):
    translator, _ = make_translator(tmp_path, {"en": {"menu": {"title": "Main Menu"}}})

    assert translator.t("menu.title") == "Main Menu"


# --- t: missing texts ------------------------------------------------------

def test_t_falls_back_to_english_when_the_key_is_missing_in_the_language(tmp_path):
    translator, state_manager = make_translator(tmp_path, {"en": {"hello": "Hello"}, "it": {}})
    state_manager.set(StateKeys.LANGUAGE, "it")

    assert translator.t("hello") == "Hello"


def test_t_falls_back_to_english_when_the_language_has_no_file(tmp_path):
    translator, state_manager = make_translator(tmp_path, HELLO)
    state_manager.set(StateKeys.LANGUAGE, "fr")

    assert translator.t("hello") == "Hello"


def test_t_returns_the_key_when_the_text_is_missing_everywhere(tmp_path):
    translator, _ = make_translator(tmp_path, HELLO)

    assert translator.t("menu.missing") == "menu.missing"


def test_t_logs_a_warning_with_the_key_when_the_text_is_missing_everywhere(tmp_path, caplog):
    translator, _ = make_translator(tmp_path, HELLO)

    with caplog.at_level(logging.WARNING):
        translator.t("menu.missing")

    assert "menu.missing" in caplog.text


# --- t: parameters ---------------------------------------------------------

def test_t_fills_in_the_parameters(tmp_path):
    translator, _ = make_translator(tmp_path, {"en": {"hello": "Hello {name}"}})

    assert translator.t("hello", name="Anna") == "Hello Anna"


def test_t_returns_the_text_as_it_is_when_a_parameter_is_missing(tmp_path):
    translator, _ = make_translator(tmp_path, {"en": {"hello": "Hello {name}"}})

    assert translator.t("hello") == "Hello {name}"
    assert translator.t("hello", other="x") == "Hello {name}"


# --- load ------------------------------------------------------------------

def test_load_a_broken_file_is_skipped_and_the_others_are_loaded(tmp_path, caplog):
    write_locale(tmp_path, "en", {"hello": "Hello"})
    (tmp_path / "it.json").write_text("{ this is not json", encoding="utf-8")
    state_manager = StateManager(EventBus())

    with caplog.at_level(logging.WARNING):
        translator = Translator(state_manager, tmp_path)

    assert "it.json" in caplog.text
    assert translator.t("hello") == "Hello"


def test_load_a_file_that_is_not_a_dictionary_is_skipped(tmp_path):
    write_locale(tmp_path, "en", {"hello": "Hello"})
    (tmp_path / "it.json").write_text("[1, 2, 3]", encoding="utf-8")
    state_manager = StateManager(EventBus())
    translator = Translator(state_manager, tmp_path)

    state_manager.set(StateKeys.LANGUAGE, "it")

    assert translator.t("hello") == "Hello"


def test_load_a_missing_directory_does_not_raise(tmp_path):
    state_manager = StateManager(EventBus())
    translator = Translator(state_manager, tmp_path / "does_not_exist")

    assert translator.t("hello") == "hello"


def test_load_only_json_files_are_loaded(tmp_path):
    write_locale(tmp_path, "en", {"hello": "Hello"})
    (tmp_path / "notes.txt").write_text("hello = ignore me", encoding="utf-8")
    state_manager = StateManager(EventBus())

    translator = Translator(state_manager, tmp_path)

    assert translator.t("hello") == "Hello"
