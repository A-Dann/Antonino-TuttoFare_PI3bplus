"""
Module containing the AIService class to handle communication with AI providers 
(Gemini, OpenRouter, Groq) supporting native tool/function calling and agentic loops.
"""

import json
import logging
import os
from typing import List, Union, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError
from openai import OpenAI

from antonino_tuttofare.main import get_current_state
from antonino_tuttofare.services import ai_tools

logger = logging.getLogger(__name__)


class AIService:
    """Service class to handle communication with AI providers (Gemini, OpenRouter, Groq) 
    and supporting native tool/function calling with full agentic loops.
    """

    def __init__(self, provider: str = "groq", model_name: Optional[str] = None):
        self.provider = provider.lower()
        self.model_name = model_name
        logger.debug(f"Initializing AIService with provider: {self.provider}")

        self.system_instruction = self._build_system_instruction()
        self.client = None
        self.chat = None
        self.messages = []
        
        self._init_client()

    @staticmethod
    def _build_system_instruction() -> str:
        """Encapsulates system instruction rules to adhere to Single Responsibility."""
        return (
            "You are Antonino Tuttofare, the voice assistant integrated into a Raspberry Pi 3B+, "
            "designed as a multi-tool device with plenty of functions.\n"
            "Maintain a friendly tone, try not going over 100 words but don't be too brief.\n"
            "You navigate through the application following a state machine. Map of states:\n"
            "1. MAIN_MENU -> DESKTOP_MODE, DUAL_AUDIO, SETTINGS, TURN_OFF (Action: CloseAiAgent)\n"
            "2. SETTINGS -> SYSTEM_INFO, WIFI_MENU, SYNC_TIME_AND_PLACE, CHANGE_LANGUAGE, MAIN_MENU\n"
            "3. WIFI_MENU -> Sub-actions and SETTINGS\n\n"
            "CRITICAL RULE: When the user asks to change menu, open a section, or navigate, "
            "you MUST invoke the `change_state` function. Do not just write text saying you changed menu.\n"
            "Always check your [CURRENT_STATE: ...] prompt context to navigate step-by-step."
        )

    def _init_client(self):
        """Initializes the specific client based on the chosen provider applying separation of concerns."""
        if self.provider == "gemini":
            self._init_gemini_client()
        elif self.provider in ["openrouter", "groq"]:
            self._init_openai_compatible_client()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'gemini', 'openrouter', or 'groq'.")

    def _init_gemini_client(self):
        """Initializes the official Google GenAI client with explicit tool settings and zero temperature."""
        self.client = genai.Client()
        self.model_name = self.model_name or "gemini-3.6-flash"
        
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.0,
            tools=ai_tools.gemini_tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            )
        )
        
        logger.debug("Creating Gemini chat session...")
        self.chat = self.client.chats.create(
            model=self.model_name,
            config=self.config
        )
        logger.debug("Gemini client initialized successfully.")

    def _init_openai_compatible_client(self):
        """Initializes OpenAI or compatible providers (Groq, OpenRouter)."""
        if self.provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
            api_key = os.getenv("OPENROUTER_API_KEY")
            self.model_name = self.model_name or "deepseek/deepseek-chat"
        elif self.provider == "groq":
            base_url = "https://api.groq.com/openai/v1"
            api_key = os.getenv("GROQ_API_KEY")
            self.model_name = self.model_name or "openai/gpt-oss-120b"

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.messages = [{"role": "system", "content": self.system_instruction}]
        logger.debug(f"OpenAI-compatible client ({self.provider}) initialized successfully.")

    def ask_audio(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        """Processes audio input bytes. Core production method."""
        logger.debug(f"Processing audio input ({len(audio_bytes)} bytes)...")
        payload = [
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ]
        return self._send_request(payload)

    def _send_request(self, payload: Union[List, str]) -> str:
        """Unified internal method to dispatch requests based on the active provider strategy."""
        try:
            current_state = get_current_state()
            state_prefix = f"[CURRENT_STATE: {current_state}]"

            logger.info("Sending request to AI Agent...")

            if self.provider == "gemini":
                return self._handle_gemini_request(state_prefix, payload)
            else:
                return self._handle_openai_request(state_prefix, payload)

        except APIError as e:
            return self._handle_api_error(e)
        except Exception as e:
            logger.error(f"Unexpected error communicating with AI Agent: {e}", exc_info=True)
            return f"Unexpected error: {e}"

    def _handle_gemini_request(self, state_prefix: str, payload: Union[List, str]) -> str:
        """Handles request formatting and response parsing specifically for Gemini."""
        if isinstance(payload, list):
            request_contents = [state_prefix] + payload
        else:
            request_contents = [state_prefix, str(payload)]

        response = self.chat.send_message(request_contents)
        
        # Agentic loop execution for Gemini function calls
        if getattr(response, "function_calls", None):
            return self._handle_gemini_function_call(response)
            
        return response.text if response.text else "No textual response from Gemini Agent."

    def _handle_openai_request(self, state_prefix: str, payload: Union[List, str]) -> str:
        """Handles request formatting and response parsing for OpenAI-compatible providers."""
        user_content = f"{state_prefix} {payload}" if not isinstance(payload, list) else [state_prefix] + payload
        
        self.messages.append({"role": "user", "content": str(user_content)})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=ai_tools.openai_tools,
            tool_choice="auto",
            temperature=0.0
        )
        choice = response.choices[0]
        
        # Check if the model wants to invoke a tool
        if choice.message.tool_calls:
            return self._handle_openai_function_call(response)

        self.messages.append(choice.message)
        return choice.message.content if choice.message.content else "No textual response from OpenAI Agent."

    def _handle_gemini_function_call(self, response) -> str:
        """Executes requested tool calls for Gemini and handles follow-up communications."""
        function_response_parts = []

        for function_call in response.function_calls:
            function_name = function_call.name
            function_args = function_call.args
            
            logger.info(f"AI requested function call: {function_name} with args {function_args}")
            tool_result = self._execute_tool(function_name, function_args)

            function_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": tool_result}
                )
            )

        logger.info("Sending all tool execution results back to Gemini (Loop)...")
        follow_up = self.chat.send_message(function_response_parts)
        return follow_up.text if follow_up.text else "Action executed successfully."

    def _handle_openai_function_call(self, response) -> str:
        """Executes requested tool calls, manages context history safely, and loops until final response."""
        choice = response.choices[0]
        
        # Safely append assistant message containing tool calls using explicit dictionary mapping
        self.messages.append({
            "role": "assistant",
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in choice.message.tool_calls
            ]
        })

        # Execute each requested tool sequentially
        for tool_call in choice.message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"AI requested function call: {function_name} with args {function_args}")
            tool_result = self._execute_tool(function_name, function_args)

            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

        logger.info("Sending all tool responses back to OpenAI provider (Agentic Loop)...")
        
        # Follow-up request to let the model generate the final response based on tool outputs
        follow_up_response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=ai_tools.openai_tools,
            tool_choice="auto",
            temperature=0.0
        )
        
        final_choice = follow_up_response.choices[0].message
        self.messages.append({
            "role": "assistant",
            "content": final_choice.content or ""
        })

        return final_choice.content if final_choice.content else "Action executed successfully."

    def _execute_tool(self, function_name: str, function_args: dict) -> str:
        """Executes the specific tool dynamically."""
        function_called = getattr(ai_tools, function_name, None)
        if callable(function_called):
            try:
                return function_called(**function_args)
            except Exception as e:
                logger.error(f"Error executing tool {function_name}: {e}")
                return f"Error executing tool: {e}"
        return f"Unknown tool: {function_name}"

    @staticmethod
    def _handle_api_error(e: APIError) -> str:
        """Centralizes API error management."""
        error_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
        if error_code == 429:
            logger.warning("AI Agent daily quota exceeded.")
            return "Free daily quota exceeded for the AI API key. Please try again tomorrow."
        logger.error(f"AI Agent API error: {e}")
        return f"AI Agent service error: {getattr(e, 'message', str(e))}"

    # =========================================================================
    # TEMPORARY DEBUG METHOD - TO BE REMOVED IN FUTURE RELEASES
    # =========================================================================
    def ask_text_test(self, prompt: str) -> str:
        """DEPRECATED / DEBUG ONLY: Sends a text prompt instead of audio.
        This method exists solely for isolated testing and will be dropped 
        when audio pipeline testing is finalized. Do not rely on this in production.
        """
        logger.warning("Using temporary debug method ask_text_test(). This will be removed in future versions.")
        return self._send_request(prompt)