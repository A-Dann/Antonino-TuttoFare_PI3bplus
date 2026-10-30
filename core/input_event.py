from dataclasses import dataclass
from typing import Optional

from core.input_actions import InputActions

@dataclass(frozen=True)
class InputEvent:
    """Represents an input event from an input device."""
    input_action: InputActions
    source: str
    value: Optional[float] = None