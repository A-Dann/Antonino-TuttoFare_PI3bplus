from dataclasses import dataclass


@dataclass(frozen=True)
class Screen:
    key: str

@dataclass(frozen=True)
class MenuItem:
    id: str
    label: str
    icon: str | None = None

@dataclass(frozen=True)
class MenuScreen(Screen):
    title: str
    options: tuple[MenuItem, ...]
