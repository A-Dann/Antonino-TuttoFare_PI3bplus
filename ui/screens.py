from dataclasses import dataclass


@dataclass
class Screen:
    key: str

@dataclass
class MenuItem:
    id: str
    label: str
    icon: str | None = None

@dataclass
class MenuScreen(Screen):
    title: str
    options: list[MenuItem]
