_MENU_REGISTRY = {}

def register_menu(key: str, options, actions):
    _MENU_REGISTRY[key] = {
        "options": options,
        "actions": actions
    }

def get_options(state_manager):
    current_menu = state_manager.get("active_menu")
    menu_data = _MENU_REGISTRY.get(current_menu)
    
    if not menu_data:
        return []
    
    return menu_data["options"]

def select_option(event_bus, state_manager, selected_option):
        current_menu = state_manager.get("active_menu")
        menu_data = _MENU_REGISTRY.get(current_menu)

        if not menu_data:
            return[]

        actions = menu_data["actions"]
        action_function = actions.get(selected_option)

        if action_function:
             action_function(event_bus, state_manager)
