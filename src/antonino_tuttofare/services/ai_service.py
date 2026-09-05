import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from antonino_tuttofare.main import get_current_state
from antonino_tuttofare.services.ai_tools import ai_tools
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

class GeminiService:
    """Service class to handle communication with the Gemini API."""

    def __init__(self, model_name: str = "gemini-3.6-flash"):
        """Initializes the Gemini client, system instructions, and generation config."""
        logger.debug("Initializing GeminiService and API client...")
        self.client = genai.Client()
        self.model_name = model_name
        
        # System instructions defining the agent's identity and behavior
        self.system_instruction = (
            """
                You are Antonino Tuttofare, the voice assistant integrated into a Raspberry Pi 3B+, a system design as a multi-tool device with plenty of functions.
                Maintain a friendly tone, try not going over 100 words but don't be too brief.
                You navigate through the application following a state machine. You know the exact map of states and commands:

                1. **MAIN_MENU**
                - **Navigation states:** `DESKTOP_MODE`, `DUAL_AUDIO`, `SETTINGS`, `TURN_OFF`.
                - **Background action:** `CloseAiAgent` (Stops the voice agent and exits).

                2. **SETTINGS** (Requires being in MAIN_MENU)
                - **Navigation states:** `SYSTEM_INFO`, `WIFI_MENU`, `SYNC_TIME_AND_PLACE`, `CHANGE_LANGUAGE`, `MAIN_MENU`.

                3. **WIFI_MENU** (Requires being in SETTINGS)
                - **Navigation states:** Sub-actions and `SETTINGS`.

                CRITICAL RULE: When the user asks to change menu, open a section, or navigate, you MUST invoke the `change_state` function. Do not just write text saying you changed menu; you must physically call the tool.
                
                Navigation rule: Always look at your CURRENT_STATE provided in the prompt to check your current position. To reach any option or submenu, you must navigate step-by-step through the correct path from where you currently are. Do not skip levels or jump straight to a target state without passing through the required intermediate menus.
            """
        )
        
        # Static configuration for all requests, including tools=[] to prevent automatic function calling warnings
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.3,
            tools = ai_tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY"
                )
            ),
        )

        # Persistent chat session to support native tool calling and context
        logger.debug("Creating Gemini chat session...")
        self.chat = self.client.chats.create(
            model=self.model_name,
            config=self.config
        )

    def ask_audio(self, audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
        """Sends an audio file to Gemini for processing. This is the primary method.
        
        Args:
            audio_bytes (bytes): The audio file loaded in memory.
            mime_type (str): The MIME type of the audio data.
            
        Returns:
            str: The textual response from the model.
        """
        logger.debug(f"Processing audio input ({len(audio_bytes)} bytes)...")
        payload = [
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type,
            ),
        ]
        return self._send_request(payload)

    def _send_request(self, payload: list | str) -> str:
        """Internal method to send the request and handle common API errors.
        
        Args:
            payload: The payload to send to Gemini (text string or list of parts).
            
        Returns:
            str: The textual response from Gemini, or an error message.
        """
        try:
            current_state = get_current_state()
            state_prefix = f"[CURRENT_STATE: {current_state}]"

            # Gestione corretta senza liste annidate
            if isinstance(payload, str):
                request_contents = [state_prefix, payload]
            elif isinstance(payload, list):
                request_contents = [state_prefix] + payload
            else:
                request_contents = [state_prefix, str(payload)]

            logger.info("Sending request to Gemini via Chat session...")
            
            response = self.chat.send_message(request_contents)

            if response.function_calls:
                for function_call in response.function_calls:
                    name = function_call.name
                    args = function_call.args
                    
                    logger.info(f"AI requested function call: {name} with args {args}")
                    
                    # Esegui il tool in locale
                    tool_result_str = ""
                    if name == "change_state":
                        from antonino_tuttofare.services.ai_tools import change_state
                        tool_result_str = change_state(**args)
                    elif name == "execute_action":
                        from antonino_tuttofare.services.ai_tools import execute_action
                        tool_result_str = execute_action(**args)
                    else:
                        tool_result_str = f"Unknown tool: {name}"

                    # Rimanda l'esito del tool alla chat per mantenere la sincronia
                    function_response_part = types.Part.from_function_response(
                        name=name,
                        response={"result": tool_result_str}
                    )
                    
                    logger.info("Sending tool execution result back to Gemini chat...")
                    follow_up_response = self.chat.send_message([function_response_part])
                    
                    if follow_up_response.text:
                        return follow_up_response.text
                    return tool_result_str

            # Fallback se non ci sono funzioni attivate
            logger.info("Response received successfully from Gemini.")
            return response.text if response.text else "Comando eseguito."
        
        except APIError as e:
            if getattr(e, 'code', None) == 429:
                logger.warning("Gemini daily quota exceeded.")
                return "Free daily quota exceeded for the Gemini API key. Please try again tomorrow."
            else:
                logger.error(f"Gemini API error: {e}")
                return f"Gemini service error: {getattr(e, 'message', str(e))}"
                
        except Exception as e:
            logger.error(f"Unexpected error communicating with Gemini: {e}", exc_info=True)
            return f"Unexpected error: {e}"

    def _handle_function_calls(self, response) -> str | None:
            """Checks and executes any function calls requested by the AI model.
            
            Args:
                response: The response object returned by the Gemini API.
                
            Returns:
                str | None: The result of the function execution if called, or None otherwise.
            """
            if not response.function_calls:
                return None

            for function_call in response.function_calls:
                name = function_call.name
                args = function_call.args
                
                logger.info(f"AI requested function call: {name} with args {args}")
                
                if name == "change_state":
                    from antonino_tuttofare.services.ai_tools import change_state
                    return change_state(**args)
                    
                elif name == "execute_action":
                    from antonino_tuttofare.services.ai_tools import execute_action
                    return execute_action(**args)
                    
            return None

    def ask_text_test(self, prompt: str) -> str:
        """Sends a text prompt to Gemini. For testing purposes only.
        
        Args:
            prompt (str): The text input.
            
        Returns:
            str: The textual response from the model.
        """
        logger.debug("Processing text input (testing mode)...")
        return self._send_request(prompt)