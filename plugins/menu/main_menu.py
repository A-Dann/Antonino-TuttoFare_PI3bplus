from ui.navigation import register_menu, register_screen
from ui.screens import MenuItem, MenuScreen

def _action_desktop_mode(event_bus, state_manager):
    print("Desktop Mode")

def _action_dual_audio(event_bus, state_manager):
    print("Dual Audio")

def _action_settings(event_bus, state_manager):
    print("Settings")

def _action_exit(event_bus, state_manager):
    print("Turn Off")
    state_manager.set("active_screen", None)

main_screen = MenuScreen(
    key="Main",
    title="Main Menu",
    options=[
        MenuItem(id="desktop", label='menu_desktop_mode'),
        MenuItem(id="dual_audio", label='menu_dual_audio'),
        MenuItem(id="settings", label='menu_settings'),
        MenuItem(id="exit", label='menu_exit')
    ],
    selected_option=0
)

actions = {
    "desktop": _action_desktop_mode,
    "dual_audio": _action_dual_audio,
    "settings": _action_settings,
    "exit": _action_exit
}

register_screen(main_screen, actions)