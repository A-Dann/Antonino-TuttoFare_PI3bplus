import logging
from antonino_tuttofare.services.ai_service import ask_gemini
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

def run():
    logger.info("AI Agent menu module started.")
    print(f"\n--- {t('ai_agent')} ---")
    print("Type 'exit' to return to the main menu.")
    
    while True:
        try:
            user_input = input("\nAsk Gemini > ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue

            response = ask_gemini(user_input)
            print(f"\nGemini: {response}")
            
        except Exception as e:
            logger.error("Errore durante la comunicazione con Gemini: %s", e, exc_info=True)
            print(f"Error: {e}")