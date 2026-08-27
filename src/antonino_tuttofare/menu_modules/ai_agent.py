import logging
import threading
import time
from antonino_tuttofare.services.ai_service import ask_gemini
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

_running = False
_thread = None

def _ai_worker():
    """
    Worker principale in background. 
    Diventerà il ciclo di ascolto vocale continuo (es. wake word + microfono).
    """
    global _running
    logger.info("AI Agent background worker started.")
    
    while _running:
        # TODO Futuro: qui ci sarà l'ascolto dal microfono in background
        time.sleep(1) # Evita il consumo eccessivo della CPU sul Raspberry Pi 3B+

def start():
    global _running, _thread
    if _running:
        return
    _running = True
    _thread = threading.Thread(target=_ai_worker, daemon=True)
    _thread.start()
    logger.info("AI Agent started in background.")

def stop():
    global _running
    _running = False
    logger.info("AI Agent stop requested.")

def is_running() -> bool:
    return _running

def run_testing_console():
    """
    Ponte di testing isolato: opzione extra solo per testare l'invio di testo
    all'agente senza bloccare il flusso principale delle altre app.
    """
    print(f"\n--- {t('ai_agent')} [MODALITÀ TEST SCRITTURA] ---")
    print("Digita un messaggio per simulare il comando vocale (o 'exit' per tornare al menu).")
    
    while True:
        try:
            user_input = input("\n[TEST SIMULAZIONE VOCE] > ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue

            response = ask_gemini(user_input)
            print(f"\nGemini (Simulazione Vocale): {response}")
            
        except Exception as e:
            logger.error("Errore nel test dell'AI Agent: %s", e, exc_info=True)
            print(f"Error: {e}")