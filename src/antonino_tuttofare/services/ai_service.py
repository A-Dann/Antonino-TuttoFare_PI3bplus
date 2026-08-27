import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def ask_gemini(prompt: str) -> str:
    try:
        logger.debug("Checking API key...")
        client = genai.Client()
        
        # System instructions defining the agent's identity and behavior
        system_instruction = (
            "You are Antonino Tuttofare, the voice assistant integrated into a Raspberry Pi 3B+ "
            "system design as a multi-tool device with plenty of functions. "
            "Always reply concisely, directly, and naturally, keeping in mind that your responses "
            "will be read aloud by a Text-to-Speech (TTS) engine. "
            "Maintain a friendly tone, keep it extremely brief, and avoid long bulleted lists."
        )
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
        
        logger.info("Sending request to Gemini with system context...")
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=config,
        )
        
        logger.info("Response received successfully from Gemini.")
        return response.text

    except APIError as e:
        if e.code == 429:
            logger.warning("Gemini daily quota exceeded.")
            return "Free daily quota exceeded for the Gemini API key. Please try again tomorrow."
        else:
            logger.error("Gemini API error: %s", e)
            return f"Gemini service error: {e.message}"
            
    except Exception as e:
        logger.error("Unexpected error communicating with Gemini: %s", e, exc_info=True)
        return f"Unexpected error: {e}"