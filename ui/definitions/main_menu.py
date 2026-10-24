from plugins.menu_components.menu_logic import register_menu

def _action_desktop_mode(event_bus, state_manager):
    print("Desktop Mode")

def _action_dual_audio(event_bus, state_manager):
    print("Dual Audio")

def _action_settings(event_bus, state_manager):
    print("Settings")

def _action_exit(event_bus, state_manager):
    print("Turn Off")
    state_manager.set("active_menu", None)

options = [
    {"id": "desktop", "label": 'menu_desktop_mode'},
    {"id": "dual_audio", "label": 'menu_dual_audio'},
    {"id": "settings", "label": 'menu_settings'},
    {"id": "exit", "label": 'menu_exit'}
]

actions = {
    "desktop": _action_desktop_mode,
    "dual_audio": _action_dual_audio,
    "settings": _action_settings,
    "exit": _action_exit
}

register_menu("Main Menu", options, actions)