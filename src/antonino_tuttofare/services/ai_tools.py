"""
Module containing the tools executable by the AI agent (Function Calling).
Each function must have a descriptive docstring to allow Gemini 
to understand its purpose and required parameters.
"""

import logging
from antonino_tuttofare import main

logger = logging.getLogger(__name__)

def change_state(target_state: str) -> str:
    """MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user 
    asks to change menu, open a section, go back, or navigate anywhere. 
    Never respond with text only when a navigation intent is detected; execute this tool.
    
    Args:
        target_state: The exact string identifier of the target state. 
                      Allowed values: MAIN_MENU, SETTINGS, WIFI_MENU, DESKTOP_MODE, SYSTEM_INFO, SYNC_TIME_AND_PLACE, CHANGE_LANGUAGE, TURN_OFF.
    """
    return main.change_state(target_state)

def execute_action(action_name: str) -> str:
    """MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user 
    requests a background action or system command in the current menu.
    
    Args:
        action_name: The exact name of the action to execute. 
                     Allowed values: CloseAiAgent.
    """
    logger.info(f"Tool executed: running action {action_name}")
    if action_name == "CloseAiAgent":
        main.change_state("MAIN_MENU")
    return f"Action {action_name} executed successfully."

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
                        "enum": ["MAIN_MENU", "SETTINGS", "WIFI_MENU", "DESKTOP_MODE", "SYSTEM_INFO", "SYNC_TIME_AND_PLACE", "CHANGE_LANGUAGE", "TURN_OFF"]
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
            "description": "MANDATORY SYSTEM COMMAND. You MUST call this function immediately when the user requests a background action or system command in the current menu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_name": {
                        "type": "string",
                        "description": "The exact name of the action to execute.",
                        "enum": ["CloseAiAgent"]
                    }
                },
                "required": ["action_name"]
            }
        }
    }
]