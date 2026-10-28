_RENDER_REGISTRY = {}

def registered_renderers(screen_type, draw_function):
    _RENDER_REGISTRY[screen_type] = (draw_function)

def render_screen(state_manager):
    render_engine = state_manager.get("renderer_engine")
    if not render_engine:
        print("No renderer engine set in state manager.")
        return
    
    current_screen = state_manager.get("active_screen")
    render_function = _RENDER_REGISTRY.get(type(current_screen))
    if render_function:
        render_function(render_engine, current_screen)
    else:
        print(f"No renderer registered for screen type: {type(current_screen)}")