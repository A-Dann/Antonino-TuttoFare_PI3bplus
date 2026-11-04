from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.input_event import InputEvent


class InputInterface(ABC):
    """Contract every input device must follow.

    - start() must not block: if a thread is needed, the device creates it.
    - stop() stops the thread, restores the hardware and can be called twice.
    - A device only emits InputActions, never codes of its own.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the device, used as the source of its events."""

    @abstractmethod
    def start(self, emit: Callable[[InputEvent], None]) -> None:
        """Start the device; call emit(event) for every input."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the input interface."""
