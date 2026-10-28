import logging

log = logging.getLogger(__name__)

_RENDER_REGISTRY = {}

def register_renderer(screen_type, draw_function):
    """Register a rendering function for a specific screen type."""
    _RENDER_REGISTRY[screen_type] = draw_function

def render_screen(state_manager, navigation, renderer_engine):
    """Render the active screen using the provided engine."""
    if not renderer_engine:
        log.warning("No renderer engine provided.")
        return
    
    current_screen = navigation.get_active_screen(state_manager)
    if not current_screen:
        log.warning("No active screen found to render.")
        return

    render_function = _RENDER_REGISTRY.get(type(current_screen))
    if render_function:
        render_function(renderer_engine, current_screen)
    else:
        log.warning(f"No renderer registered for screen type: {type(current_screen)}")