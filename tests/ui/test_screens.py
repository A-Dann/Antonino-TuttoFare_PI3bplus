import dataclasses

import pytest

from ui.screens import MenuItem, MenuScreen


def test_a_screen_cannot_be_modified():
    screen = MenuScreen(key="a", title="A", options=(MenuItem("x", "X"),))

    with pytest.raises(dataclasses.FrozenInstanceError):
        screen.title = "B"


def test_the_options_of_a_menu_cannot_be_modified():
    screen = MenuScreen(key="a", title="A", options=(MenuItem("x", "X"),))

    with pytest.raises(TypeError):
        screen.options[0] = MenuItem("y", "Y")  # type: ignore[index]
