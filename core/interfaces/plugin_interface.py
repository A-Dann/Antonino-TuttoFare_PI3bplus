# core/interfaces/plugin_interface.py
from abc import ABC, abstractmethod


class Plugin(ABC):
    """Base class every plugin must extend."""

    @abstractmethod
    def start(self, ctx) -> None:
        """Called once at startup."""

    def stop(self) -> None:
        """Optional: called at shutdown."""