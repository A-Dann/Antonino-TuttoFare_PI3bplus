from __future__ import annotations

import logging
import select
import threading
from abc import abstractmethod
from collections.abc import Callable

import evdev

from core.input_actions import InputActions
from core.input_event import InputEvent
from core.interfaces.input_interface import InputInterface
from hal.input.wakeup import WakeUp

log = logging.getLogger(__name__)

JOIN_TIMEOUT = 1.0

class EvdevInput(InputInterface):
    def __init__(self, device: evdev.InputDevice) -> None:
        self._wakeup: WakeUp | None = None
        self._device = device
        self._thread: threading.Thread | None = None
        self._stop_signal = threading.Event()

    @property
    def name(self) -> str:
        return self._device.name

    @classmethod
    @abstractmethod
    def supports(cls, device: evdev.InputDevice) -> bool:
        """ Determine whether this driver supports the given input device. """
        pass

    def start(self, emit: Callable[[InputEvent], None]) -> None:
        self._wakeup = WakeUp()
        self._thread = threading.Thread(target=self.read_loop, args=(emit, self._wakeup), daemon=True)
        self._thread.start()

    def read_loop(self, emit: Callable[[InputEvent], None], wakeup: WakeUp) -> None:
        while not self._stop_signal.is_set():
            try:
                readable, _, _ = select.select([self._device.fd, wakeup.fileno()], [], [])
                if wakeup.fileno() in readable:
                    break
                if self._device.fd in readable:
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
        """ Translate a raw input event into a universal InputAction.
            Returns None if the event is not relevant. """
        pass

    def stop(self) -> None:
        self._stop_signal.set()
        if self._wakeup is not None:
            self._wakeup.set()
        if self._thread is not None:
            self._thread.join(timeout=JOIN_TIMEOUT)
            if self._thread.is_alive():
                log.warning("Thread of %s is still alive after join timed-out", self._device.name)
        self._device.close()
        self._close_wakeup()

    def _close_wakeup(self) -> None:
        if self._wakeup is None:
            return
        if self._thread is not None and self._thread.is_alive():
            return  # the thread may still use it; a later stop() will retry
        self._wakeup.close()
        self._wakeup = None
