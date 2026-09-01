import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
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
            "You are Antonino Tuttofare, the voice assistant integrated into a Raspberry Pi 3B+ "
            "system design as a multi-tool device with plenty of functions. "
            "Always reply concisely, directly, and naturally in a maximum of one or two sentences, "
            "keeping in mind that your responses will be read aloud by a Text-to-Speech (TTS) engine. "
            "Maintain a friendly tone, try not going over 100 words but don't be too brief."
        )
        
        # Static configuration for all requests, including tools=[] to prevent automatic function calling warnings
        self.config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            temperature=0.7,
            tools=[],
        )

    def _send_request(self, contents: list | str) -> str:
        """Internal method to send the request and handle common API errors.
        
        Args:
            contents: The payload to send to Gemini (text string or list of parts).
            
        Returns:
            str: The textual response from Gemini, or an error message.
        """
        try:
            logger.info("Sending request to Gemini...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=self.config,
            )
            logger.info("Response received successfully from Gemini.")
            return response.text

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
            "Rispondi a questa richiesta vocale:"
        ]
        return self._send_request(payload)

    def ask_text_test(self, prompt: str) -> str:
        """Sends a text prompt to Gemini. For testing purposes only.
        
        Args:
            prompt (str): The text input.
            
        Returns:
            str: The textual response from the model.
        """
        logger.debug("Processing text input (testing mode)...")
        return self._send_request(prompt)