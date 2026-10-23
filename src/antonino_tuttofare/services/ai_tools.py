"""
Module containing the tools executable by the AI agent (Function Calling).
Each function must have a descriptive docstring to allow Gemini 
to understand its purpose and required parameters.
"""

import logging
from antonino_tuttofare import state
from antonino_tuttofare.services import wifi_service

logger = logging.getLogger(__name__)

# Callback reference to stop the AI agent without circular imports
_close_agent_callback = None

def register_close_agent_callback(callback):
    """Registers the callback function to stop the AI agent background thread."""
    global _close_agent_callback
    _close_agent_callback = callback

# =====================================================================
# 1. NAVIGATION STATES (change_state)
# =====================================================================

def change_state(target_state: str) -> str:
    """MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user 
    asks to change menu, open a section, go back, or navigate anywhere.
    
    Args:
        target_state: The exact string identifier of the target state.
    """
    return state.set_current_state(target_state)

# =====================================================================
# 2. OPERATIONAL ACTIONS & REGISTRY (execute_action)
# =====================================================================

def _action_close_agent():
    if _close_agent_callback:
        _close_agent_callback()
    state.set_current_state("MAIN_MENU")
    return "AI Agent closed successfully."

def _action_wifi_disconnect():
    success = wifi_service.disconnect_current_network()
    state.set_current_state("WIFI_MENU")
    return "Wi-Fi disconnesso con successo." if success else "Errore durante la disconnessione."

# Centralized map of executable actions
ACTION_REGISTRY = {
    "CloseAiAgent": _action_close_agent,
    "WifiDisconnect": _action_wifi_disconnect,
}

def execute_action(action_name: str) -> str:
    """MANDATORY SYSTEM COMMAND. Executes a background operational command."""
    logger.info(f"Tool executed: running action {action_name}")
    
    handler = ACTION_REGISTRY.get(action_name)
    if handler:
        return handler()
        
    return f"Error: Unknown action '{action_name}'."

# =====================================================================
# 3. AI TOOL SCHEMAS (Gemini & OpenAI definitions)
# =====================================================================

gemini_tools = [change_state, execute_action]

openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "change_state",
            "description": "MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user asks to change menu, open a section, go back, or navigate anywhere.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_state": {
                        "type": "string",
                        "description": "The exact string identifier of the target state.",
                        "enum": state.VALID_STATES
                    }
                },
                "required": ["target_state"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_action",
            "description": "MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user requests an operational command or background action like closing the agent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_name": {
                        "type": "string",
                        "description": "The exact name of the action to execute.",
                        "enum": ["CloseAiAgent", "WifiDisconnect"]
                    }
                },
                "required": ["action_name"]
            }
        }
    }
]