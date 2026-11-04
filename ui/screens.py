from dataclasses import dataclass


@dataclass
class MenuItem:
    id: str
    label: str
    icon: str | None = None

@dataclass
class MenuScreen:
    key: str
    title: str
    options: list[MenuItem]
