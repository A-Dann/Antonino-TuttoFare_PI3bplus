"""
Utility module for offline Speech-to-Text (STT) using faster-whisper 
and Text-to-Speech (TTS) using pyttsx3, with dedicated speech language handling.
"""

import logging
import os
import tempfile
from typing import Optional
from faster_whisper import WhisperModel
import pyttsx3

from antonino_tuttofare import config
from antonino_tuttofare.utility import audio_utils
from antonino_tuttofare.utility.files_utils import read_json, write_json

logger = logging.getLogger(__name__)


def get_speech_language() -> str:
    """Retrieves the speech recognition language preference safely 
    from the unified configuration file using files_utils.read_json.
    """
    try:
        if config.LANGUAGE_CONFIG_PATH.exists():
            data = read_json(config.LANGUAGE_CONFIG_PATH, default_value={})
            if isinstance(data, dict):
                # Priorità: speech_language -> language -> DEFAULT_LANGUAGE
                return data.get("speech_language", data.get("language", config.DEFAULT_LANGUAGE))
    except Exception as e:
        logger.debug(f"Could not read speech language configuration: {e}")
    
    return config.DEFAULT_LANGUAGE


def set_speech_language(lang_code: str) -> None:
    """Saves the speech recognition language preference persistently 
    to the unified configuration file using files_utils.
    """
    try:
        data = {}
        if config.LANGUAGE_CONFIG_PATH.exists():
            data = read_json(config.LANGUAGE_CONFIG_PATH, default_value={})
            if not isinstance(data, dict):
                data = {}
        
        data["speech_language"] = lang_code
        write_json(config.LANGUAGE_CONFIG_PATH, data)
        logger.info(f"Speech language successfully updated to: {lang_code}")
    except Exception as e:
        logger.error(f"Failed to save speech language: {e}")


class SpeechConverter:
    """Handles offline audio-to-text transcription and text-to-speech synthesis."""

    def __init__(self):
        logger.debug("Initializing offline SpeechConverter...")
        model_size = "base"
        try:
            logger.info(f"Loading faster-whisper model ({model_size})...")
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.whisper_model = None

        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 165)
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3 TTS engine: {e}")
            self.tts_engine = None

    def _transcribe_speech(self, speech_data) -> Optional[str]:
        """Converts raw audio array into WAV bytes and transcribes it to text using Whisper."""
        if speech_data is None:
            return None

        wav_bytes = audio_utils.audio_to_wav_bytes(
            speech_data, sample_rate=16000
        )

        logger.info("Transcribing audio locally using Whisper...")
        return self.audio_to_text(wav_bytes)


    def speak(self, text: str) -> None:
        """Synthesizes the text and plays it directly through the system speakers in real-time.
        Useful for local playback on the device without handling files or external commands.
        """
        if not self.tts_engine:
            logger.error("TTS engine is not initialized.")
            return

        logger.info(f"Speaking text offline: '{text[:30]}...'")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"Error during offline speech synthesis: {e}", exc_info=True)

    def audio_to_text(self, audio_bytes: bytes) -> Optional[str]:
        """Converts text into raw binary audio data (WAV-formatted bytes).
        Useful if you need to save the audio to a file, send it over a network, 
        or stream it to a remote client instead of playing it locally.
        
        Args:
            audio_bytes: The WAV-formatted audio bytes in memory.
            
        Returns:
            str: The transcribed text, or None if transcription fails.
        """
        if not self.whisper_model:
            logger.error("Whisper model is not initialized.")
            return None

        speech_lang = get_speech_language()
        logger.info(f"Transcribing audio offline using speech language: {speech_lang}")

        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name

            try:
                segments, _ = self.whisper_model.transcribe(temp_path, language=speech_lang, beam_size=5, vad_filter=True, temperature=0.0)
                text = " ".join([segment.text for segment in segments]).strip()
                return text
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"Error during offline audio transcription: {e}", exc_info=True)
            return None

    def text_to_audio(self, text: str) -> Optional[bytes]:
        """Converts text into speech audio bytes locally using pyttsx3."""
        if not self.tts_engine:
            logger.error("TTS engine is not initialized.")
            return None

        logger.info(f"Synthesizing text offline: '{text[:30]}...'")
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_path = temp_audio.name

            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()

            with open(temp_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            if os.path.exists(temp_path):
                os.remove(temp_path)

            return audio_bytes
        except Exception as e:
            logger.error(f"Error during offline text-to-speech synthesis: {e}", exc_info=True)
            return None