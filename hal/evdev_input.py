from __future__ import annotations

import logging
import select
import threading
from abc import abstractmethod
from collections.abc import Callable

import evdev

from core.input_actions import InputActions
from core.input_event import InputEvent
from hal.input_interface import InputInterface

log = logging.getLogger(__name__)

class EvdevInput(InputInterface):
    def __init__(self, device: evdev.InputDevice) -> None:
        self._device = device
        self._thread: threading.Thread | None = None
        self._stop_signal = threading.Event()

    @property
    def name(self) -> str:
        return self._device.name

    @classmethod
    @abstractmethod
    def supports(cls, device: evdev.InputDevice) -> bool:
        pass

    def start(self, emit: Callable[[InputEvent], None]) -> None:
        self._thread = threading.Thread(target=self.read_loop, args=(emit,), daemon=True)
        self._thread.start()

    def read_loop(self, emit: Callable[[InputEvent], None]) -> None:
        while not self._stop_signal.is_set():
            try:
                selected_fd, _, _ = select.select([self._device.fd],[],[], 0.5)
                if self._device.fd in selected_fd:
                    for raw_event in self._device.read():
                        self.emit_action(raw_event, emit)

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

    @abstractmethod
    def translate_event_to_action(self, raw_event: evdev.InputEvent) -> InputActions | None:
        pass

    def stop(self) -> None:
        self._stop_signal.set()
        if self._thread is not None:
            self._thread.join(timeout=1)
        self._device.close()

