from dataclasses import dataclass
from typing import Any

from core.state_keys import StateKeys


@dataclass(frozen=True)
class StateChanged:
    """Payload of the STATE_CHANGED event: which key changed and its new value."""
    key: StateKeys
    value: Any
