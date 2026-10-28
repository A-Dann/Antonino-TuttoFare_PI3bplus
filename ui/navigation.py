import logging

log = logging.getLogger(__name__)

_SCREEN_REGISTRY = {}
_ACTIONS_REGISTRY = {}

def register_screen(screen, actions=None):
    _SCREEN_REGISTRY[screen.key] = screen
    if actions:
        _ACTIONS_REGISTRY[screen.key] = actions

def get_active_screen(state_manager):
    current_key = state_manager.get("active_screen")
    return _SCREEN_REGISTRY.get(current_key)

def execute_action(event_bus, state_manager, action_id: str):
    current_key = state_manager.get("active_screen")
    actions = _ACTIONS_REGISTRY.get(current_key, {})

    action = actions.get(action_id)
    if action:
        action(event_bus, state_manager)
    else:
        print(f"No action found for id: {action_id} on screen: {current_key}")