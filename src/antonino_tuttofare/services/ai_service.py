import os
from google import genai
from google.genai import types
from antonino_tuttofare.config import CONFIG_DIR
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)

KEY_PATH = CONFIG_DIR / "gemini.key"

def ask_gemini(prompt: str) -> str:
    logger.debug("Verifica presenza chiave API...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and KEY_PATH.exists():
        api_key = KEY_PATH.read_text().strip()

    if not api_key:
        logger.error("API key mancante in %s", KEY_PATH)
        raise ValueError(f"API key missing. Save it in: {KEY_PATH}")

    try:
        logger.info("Inizializzazione client GenAI...")        
        client = genai.Client(api_key=api_key)
        
        # Aumentato il limite a 4096 token per evitare risposte tagliate
        config = types.GenerateContentConfig(
            max_output_tokens=4096,
        )
        
        logger.debug("Invio richiesta HTTP rapida a Gemini...")
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=config,
        )
        
        logger.info("Risposta ricevuta con successo da Gemini.")
        return response.text if response.text else ""
    except Exception as e:
        logger.error("Gemini API communication error: %s", e, exc_info=True)
        raise e