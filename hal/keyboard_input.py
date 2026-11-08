from __future__ import annotations

import logging
import select
import threading
from collections.abc import Callable

import evdev

from core.input_actions import InputActions
from core.input_event import InputEvent
from hal.input_interface import InputInterface

log = logging.getLogger(__name__)

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

    def __init__(self, device: evdev.InputDevice) -> None:
        self._device = device
        self._thread = None
        self._stop_signal = threading.Event()

    @property
    def name(self) -> str:
        return self._device.name

    def start(self, emit) -> None:
        self._thread = threading.Thread(target=self.read_loop, args=(emit,), daemon=True)
        self._thread.start()

    def read_loop(self, emit) -> None:
        while not self._stop_signal.is_set():
            try:
                selected_fd, _, _ = select.select([self._device.fd],[],[], 0.5)
                if self._device.fd in selected_fd:
                    for keyboard_event in self._device.read():
                        self.emit_action(keyboard_event, emit)

            except BlockingIOError:
                log.debug("No events available: %s", self._device.name)
            except OSError:
                log.exception("Something went wrong with: %s", self._device.name)
                break

    def emit_action(self, raw_event: evdev.InputEvent, emit: Callable[[InputEvent], None]) -> None:
        input_action = self.translate_event_to_action(raw_event)

        if input_action is None:
            return

        input_event = InputEvent(input_action, self.name)
        emit(input_event)

    def translate_event_to_action(self, raw_event: evdev.InputEvent) -> InputActions | None:
        if raw_event.type != evdev.ecodes.EV_KEY:
            return None

        event_key = raw_event.code
        if event_key not in self.keys_mapping:
            return None

        input_action = self.keys_mapping.get(event_key)

        if raw_event.value == KEY_RELEASED:
            return None

        if raw_event.value == KEY_REPEATED and input_action not in self.can_be_repeated:
            return None

        return input_action

    def stop(self) -> None:
        self._stop_signal.set()
        if self._thread is not None:
            self._thread.join(timeout=1)
        self._device.close()
