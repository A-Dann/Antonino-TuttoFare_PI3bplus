from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.event_bus import EventBus
from core.state_keys import StateKeys
from core.state_manager import StateManager
from plugins.menu.language_menu import language_actions


@pytest.mark.parametrize("language", ["en", "it", "es"])
def test_choosing_a_language_sets_it_in_the_state(language):
    state_manager = StateManager(EventBus())
    state_manager.set(StateKeys.LANGUAGE, "fr")  # start from a different language
    ctx = SimpleNamespace(state_manager=state_manager)

    language_actions[language](ctx)

    assert state_manager.get(StateKeys.LANGUAGE) == language


def test_back_goes_to_the_parent_screen():
    ctx = SimpleNamespace(navigator=Mock())

    language_actions["back"](ctx)

    ctx.navigator.go_back.assert_called_once_with()
