from core.interfaces.display_interface import DisplayInterface

CLEAR_SEQUENCE = "\033[2J\033[H"


class ConsoleDisplay(DisplayInterface):
    @property
    def name(self) -> str:
        return "Console"

    def start(self) -> None:
        pass

    def show_menu(self, title: str, options: list[str], selected_index: int) -> None:
        self.clear_screen()
        print(f"{title}\n")
        for i, option in enumerate(options):
            prefix = "> " if i == selected_index else "  "
            print(f"{prefix}{option}")

    def clear_screen(self):
        print(CLEAR_SEQUENCE, end="")

    def stop(self) -> None:
        pass
