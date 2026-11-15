from __future__ import annotations

from abc import ABC, abstractmethod


class DisplayInterface(ABC):
    """Contract every display backend must follow.

    A display is passive: it draws what it is told and never decides
    when to redraw or what to show. It is only used from the main thread,
    so implementations do not need to be thread-safe.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the display backend."""

    @abstractmethod
    def start(self) -> None:
        """Prepare the display."""

    @abstractmethod
    def show_menu(self, title: str, options: list[str], selected_index: int) -> None:
        """Draw a menu, replacing whatever was on screen before.

        Each implementation is responsible for erasing the previous content.

        title: text shown at the top.
        options: the label of each entry, in order.
        selected_index: index in options of the highlighted entry.
        """

    @abstractmethod
    def clear_screen(self) -> None:
        """Remove everything currently drawn."""

    @abstractmethod
    def stop(self) -> None:
        """Release the display. Must be safe to call more than once."""
