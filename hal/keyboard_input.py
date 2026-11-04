from __future__ import annotations

import evdev

from core.input_actions import InputActions
from hal.input_interface import InputInterface

KEY_RELEASED = 0
KEY_PRESSED = 1
KEY_REPEATED = 2

class KeyboardInput(InputInterface):
    keys_mapping = {
        evdev.ecodes.KEY_UP: InputActions.UP,
        evdev.ecodes.KEY_DOWN: InputActions.DOWN,
        evdev.ecodes.KEY_LEFT: InputActions.LEFT,
        evdev.ecodes.KEY_RIGHT: InputActions.RIGHT,
        evdev.ecodes.KEY_ENTER: InputActions.SELECT,
        evdev.ecodes.KEY_BACKSPACE: InputActions.BACK,
        evdev.ecodes.KEY_ESC: InputActions.BACK,
    }
    can_be_repeated = frozenset({
        InputActions.UP,
        InputActions.DOWN,
        InputActions.LEFT,
        InputActions.RIGHT,
    })

    @property
    def name(self):
        return "Keyboard"

    def start(self, emit):
        pass

    def translate_event_to_action(self, input_event: evdev.InputEvent) -> InputActions | None:
        if input_event.type != evdev.ecodes.EV_KEY:
            return None

        event_key = input_event.code
        if event_key not in self.keys_mapping:
            return  None

        input_action = self.keys_mapping.get(event_key)

        if input_event.value == KEY_RELEASED:
            return None

        if input_event.value == KEY_REPEATED and input_action not in self.can_be_repeated:
            return None

        return input_action


    def stop(self):
        pass
