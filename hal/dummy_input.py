from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Callable

from core.input_event import InputEvent
from hal.input_interface import InputInterface

if TYPE_CHECKING:
    from core.input_actions import InputActions


class DummyInput(InputInterface):
    def __init__(self, actions: list[InputActions], delay: float = 0.1) -> None:
        self._actions = actions
        self._delay = delay
        self._thread = None
        self._stop_signal = threading.Event()

    @property
    def name(self):
        return "Dummy"
    
    def start(self, emit: Callable[[InputEvent], None]) -> None:
        self._thread = threading.Thread(target=self._emit_actions, args=(emit,), daemon=True)
        self._thread.start()

    def _emit_actions(self, emit: Callable[[InputEvent], None]) -> None:
        for action in self._actions:
            if self._stop_signal.is_set():
                return
            event = InputEvent(input_action=action, source=self.name)
            emit(event)
            self._stop_signal.wait(self._delay)

    def stop(self) -> None:
        self._stop_signal.set()
        if self._thread is not None:
            self._thread.join(timeout=1)