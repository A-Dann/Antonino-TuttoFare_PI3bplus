from dataclasses import dataclass
from typing import Optional

@dataclass
class MenuItem:
    id: str
    label: str
    icon: Optional[str] = None

@dataclass
class MenuScreen:
    key: str
    title: str
    options: list[MenuItem]