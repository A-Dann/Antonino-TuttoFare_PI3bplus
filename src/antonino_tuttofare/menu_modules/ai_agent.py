import logging
import threading

from antonino_tuttofare.config import WAKEWORD_DIR_PATH
from antonino_tuttofare.state import get_current_state
from antonino_tuttofare.utility import audio_utils
from antonino_tuttofare.services.ai_service import AIService
from antonino_tuttofare.utility.i18n import t
from antonino_tuttofare.utility.speech_utils import SpeechConverter

logger = logging.getLogger(__name__)

wakeword_antonino = str(WAKEWORD_DIR_PATH / "antonino.onnx")
_running = False
_thread = None
_stop_event = threading.Event()

def check_hardware_availability() -> bool:
    """Verifies if both microphone and speakers are available on the system."""
    if not audio_utils.check_microphone():
        logger.warning("No microphone found. AI Agent will not start.")
        # TODO Add graphic error message
        return False

    if not audio_utils.check_speakers():
        logger.warning("No speakers/output devices found. AI Agent will not start.")
        # TODO Add graphic error message
        return False

    return True


def start() -> None:
    """Validates hardware requirements and starts the AI Agent worker thread."""
    if not check_hardware_availability():
        return

    global _running, _thread, _stop_event
    if _running:
        return
    
    _running = True
    _stop_event.clear()
    _thread = threading.Thread(target=_ai_worker, daemon=True)
    _thread.start()
    logger.info("AI Agent started in background.")


def stop() -> None:
    """Signals the background worker loop to stop running."""
    global _running, _stop_event
    _running = False
    _stop_event.set()
    logger.info("AI Agent stop requested.")


def is_running() -> bool:
    """Returns the current running status of the AI Agent."""
    return _running


def _ai_worker() -> None:
    """Main background worker loop that handles wake word detection,
    speech recording, and communication with the Gemini service.
    """
    logger.info("AI Agent background worker started.")

    try:
        ai_service = AIService()
        speech_converter = SpeechConverter()
        logger.info("AIService and SpeechConverter initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize AI Agent services: {e}", exc_info=True)
        global _running
        _running = False
        return

    while _running:
        try:
            # Start passive listening for the wake word
            stream = audio_utils.listen_for_key_word(
                wakeword_antonino, sample_rate=16000, channels=1, stop_event=_stop_event
            )
            
            # If the stream fails to initialize, wait briefly before retrying
            if stream is None:
                threading.Event().wait(1.0)
                continue

            # Keep the loop alive while the stream is active
            while _running and stream.active:
                threading.Event().wait(0.1)

            # If the user requested to stop, break out of the loop
            if not _running:
                break

            # Wake word detected, now record the active user command
            logger.info("Wake word triggered. Recording user speech...")
            speech_data = audio_utils.record_speech(
                sample_rate=16000, channels=1, silence_limit=1.5, stop_event=_stop_event
            )

            # Transcribe recorded audio into text using the dedicated helper
            wav_bytes = audio_utils.audio_to_wav_bytes(speech_data, sample_rate=16000)
            user_text = speech_converter.audio_to_text(wav_bytes)

            if user_text:
                print(f"\nUser: {user_text}")

                # Send the transcribed text to the AI service
                logger.info("Sending transcribed text to AI service...")
                response_text = ai_service._send_request(user_text)
                logger.info(f"AI response received: {response_text}")
                
                # Output the assistant's reply and speak it directly
                print(f"\nAntonino: {response_text}\n")
                speech_converter.speak(response_text)

        except Exception as worker_err:
            logger.error(
                f"Error occurred in AI Agent background worker: {worker_err}",
                exc_info=True,
            )
            threading.Event().wait(1.0)

    logger.info("AI Agent background worker stopped.")

def run_testing_console() -> None:
    """Isolated interactive testing console to send text prompts directly to the AI service
    without stopping the background worker loop.
    """
    print(f"\n--- {t('ai_agent')} [TEXT TESTING MODE] ---")
    print("Type a message to simulate a voice command, or type 'exit' to return to the menu.")
    print("Note: The background audio agent keeps running while you test here.\n")

    # Istanziamo un servizio dedicato per il debug testuale
    test_service = AIService()

    while True:
        try:
            # Recupera dinamicamente lo stato corrente per mostrarlo nel prompt
            current_state = get_current_state()
            user_input = input(f"\n[{current_state}] [VOICE SIMULATION TEST] > ").strip()
            
            if user_input.lower() == "exit":
                print("Exiting testing console. Returning to menu...")
                break
                
            if not user_input:
                continue

            # Invia il prompt di testo di debug sfruttando il metodo dedicato
            response = test_service.ask_text_test(user_input)
            print(f"\nAntonino (Debug Simulation): {response}")

        except Exception as e:
            logger.error("Error in AI Agent test: %s", e, exc_info=True)
            print(f"Error: {e}")