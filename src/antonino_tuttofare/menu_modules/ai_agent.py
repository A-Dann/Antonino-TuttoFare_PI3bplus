import logging
import threading

from antonino_tuttofare.config import WAKEWORD_DIR_PATH
from antonino_tuttofare.utility import audio_utils
from antonino_tuttofare.services.ai_service import GeminiService
from antonino_tuttofare.utility.i18n import t

logger = logging.getLogger(__name__)

wakeword_antonino = str(WAKEWORD_DIR_PATH / "antonino.onnx")
_running = False
_thread = None

# Initialize the Gemini service instance for the background worker
_ai_service = GeminiService()

def start() -> None:
    """Checks for microphone availability and starts the AI Agent in a background thread."""
    if not audio_utils.check_microphone():
        logger.warning("No microphone found. AI Agent will not start.")
        # TODO: Add graphic warning sign
        return

    global _running, _thread
    if _running:
        return
    
    _running = True
    _thread = threading.Thread(target=_ai_worker, daemon=True)
    _thread.start()
    logger.info("AI Agent started in background.")


def stop() -> None:
    """Signals the background worker loop to stop running."""
    global _running
    _running = False
    logger.info("AI Agent stop requested.")


def is_running() -> bool:
    """Returns the current running status of the AI Agent.

    Returns:
        bool: True if the agent is running, False otherwise.
    """
    return _running


def _ai_worker() -> None:
    """Main background worker loop that handles wake word detection,
    speech recording, and communication with the Gemini service.
    """
    global _running
    logger.info("AI Agent background worker started.")

    while _running:
        try:
            # Start passive listening for the wake word
            stream = audio_utils.listen_for_key_word(
                wakeword_antonino, sample_rate=16000, channels=1
            )
            
            # If the stream fails to initialize, wait briefly before retrying
            if stream is None:
                threading.Event().wait(1.0)
                continue

            # Keep the loop alive while the stream is active
            while _running and stream.active:
                threading.Event().wait(0.1)

            # If stopped externally, break out of the loop
            if not _running:
                if stream.active:
                    stream.stop()
                    stream.close()
                break

            # Wake word detected, now record the active user command
            logger.info("Wake word triggered. Recording user speech...")
            speech_data = audio_utils.record_speech(
                sample_rate=16000, channels=1, silence_limit=1.5
            )

            if speech_data is not None:
                # Convert NumPy audio array into WAV-formatted bytes in memory
                wav_bytes = audio_utils.audio_to_wav_bytes(
                    speech_data, sample_rate=16000
                )

                # Send the audio payload to Gemini using the new service method
                logger.info("Sending recorded audio to Gemini service...")
                response_text = _ai_service.ask_audio(wav_bytes)
                logger.info(f"Gemini response received: {response_text}")
                
                # Output the assistant's reply directly to the console interface
                print(f"\nAntonino: {response_text}\n")
                
                # TODO: Pass the response text to the Text-to-Speech (TTS) engine

        except Exception as worker_err:
            logger.error(
                f"Error occurred in AI Agent background worker: {worker_err}",
                exc_info=True,
            )
            threading.Event().wait(1.0)

    logger.info("AI Agent background worker stopped.")

def run_testing_console() -> None:
    """Isolated testing console to send text prompts directly to the Gemini service
    without blocking other application workflows.
    """
    print(f"\n--- {t('ai_agent')} [TEXT TESTING MODE] ---")
    print("Type a message to simulate a voice command (or 'exit' to return to the menu).")

    # Instantiate a local service instance specifically for the testing console
    test_service = GeminiService()

    while True:
        try:
            user_input = input("\n[VOICE SIMULATION TEST] > ").strip()
            if user_input.lower() == "exit":
                break
            if not user_input:
                continue

            # Send the test text prompt through the Gemini service
            response = test_service.ask_text_test(user_input)
            print(f"\nGemini (Voice Simulation): {response}")

        except Exception as e:
            logger.error("Error in AI Agent test: %s", e, exc_info=True)
            print(f"Error: {e}")