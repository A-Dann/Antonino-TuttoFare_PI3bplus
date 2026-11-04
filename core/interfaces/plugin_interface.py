# core/interfaces/plugin_interface.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import AppContext

class Plugin(ABC):
    """Base class every plugin must extend."""

    @abstractmethod
    def start(self, ctx: AppContext) -> None:
        """Called once at startup."""

    def stop(self) -> None:
        """Optional: called at shutdown."""
