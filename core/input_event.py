from dataclasses import dataclass

from core.input_actions import InputActions


@dataclass(frozen=True)
class InputEvent:
    """Represents an input event from an input device."""
    action: InputActions
    source: str
    value: float | None = None
