from pathlib import Path
import time
import io
import wave
import numpy as np

import sounddevice as sd
from openwakeword.model import Model
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)


def check_microphone() -> bool:
    """Checks for the presence of at least one available audio input device (microphone)
    on the system.

    Returns:
        bool: True if at least one microphone is found, False otherwise.
    """
    try:
        # Query all audio devices registered in the operating system
        devices = sd.query_devices()

        # Filter devices keeping only those with at least one input channel
        input_devices = [d for d in devices if d["max_input_channels"] > 0]

        if len(input_devices) > 0:
            logger.info(f"Detected {len(input_devices)} available microphones.")
            return True
        else:
            logger.warning("No microphone detected on the system.")
            return False

    except Exception as e:
        logger.error(f"Error occurred while checking audio devices: {e}")
        return False


def listen_for_key_word(
    keyword: str, sample_rate: int = 16000, channels: int = 1
):
    """Starts an audio input stream to listen for a specific wake word using openWakeWord.

    Args:
        keyword (str): The name or path of the wake word model to load.
        sample_rate (int): The audio sampling rate in Hz (default 16000).
        channels (int): Number of audio channels (default 1).

    Returns:
        sd.InputStream or None: The running audio stream object if successful, None otherwise.
    """
    try:
        # Initialize the openWakeWord model with the specified keyword model
        oww_model = Model(wakeword_model_paths=[keyword])

        model_name = Path(keyword).stem
        
        logger.info(
            f"OpenWakeWord model loaded successfully for keyword: '{model_name}'"
        )

        detected = False

        def audio_callback(indata, frames, time_info, status):
            """Callback function executed by sounddevice for each incoming audio chunk."""
            nonlocal detected

            if status:
                logger.warning(f"Audio stream status warning: {status}")

            try:
                # Convert the raw input data buffer into a NumPy array of 16-bit integers
                audio_chunk = np.frombuffer(indata, dtype=np.int16)
                
                # Compute prediction scores using openWakeWord model
                prediction = oww_model.predict(audio_chunk)
                score = prediction.get(model_name, 0.0)

                # Log real-time score if above noise floor threshold
                if score > 0.01:
                    logger.info(f"Score rilevato: {score:.4f}")
                    
                # Check if the confidence score exceeds the detection threshold
                if score > 0.5:
                    logger.info(
                        f"Wake word '{model_name}' detected! Score: {score:.2f}"
                    )
                    detected = True

            except Exception as cb_err:
                logger.error(
                    f"Error during audio processing in callback: {cb_err}"
                )

        # Open the continuous input stream using a fixed block size for openWakeWord
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback,
            dtype=np.int16,
            blocksize=1280,
        )

        stream.start()
        logger.info("Passive listening audio stream started successfully.")

        # External control loop to safely stop and close
        while stream.active:
            if detected:
                stream.stop()
                stream.close()
                break
            time.sleep(0.05)

        return stream

    except Exception as e:
        logger.error(f"Error starting passive listening stream: {e}")
        return None


def record_speech(
    sample_rate: int = 16000, channels: int = 1, silence_limit: float = 1.5
    ) -> np.ndarray | None:
    """Records active speech dynamically, stopping automatically when silence is detected.

    Args:
        sample_rate (int): Audio sampling rate in Hz (default 16000).
        channels (int): Number of audio channels (default 1).
        silence_limit (float): Seconds of continuous silence required to stop recording.

    Returns:
        np.ndarray or None: The recorded audio data array, or None if an error occurs.
    """
    try:
        logger.info("Listening for command...")
        
        audio_chunks = []
        is_speaking = False
        silent_chunks = 0
        volume_threshold = 500
        silence_limit_seconds = silence_limit
        chunk_duration = 0.1
        max_silent_chunks = int(silence_limit_seconds / chunk_duration)
        chunk_size = int(sample_rate * chunk_duration)

        def callback(indata, frames_count, time_info, status):
            """Callback function to process audio chunks and detect speech activity."""
            nonlocal is_speaking, silent_chunks
            if status:
                logger.warning(f"Audio stream status warning: {status}")

            try:
                # Convert the raw input data buffer into a NumPy array of 16-bit integers
                audio_chunk = np.frombuffer(indata, dtype=np.int16)

                # Calculate the volume of the audio chunk using absolute mean value
                chunk_volume = np.abs(audio_chunk).mean()

                # Determine if speech is present or if it's silence
                if chunk_volume > volume_threshold:
                    is_speaking = True
                    silent_chunks = 0  # Reset silence counter if speech is detected
                elif is_speaking:
                    silent_chunks += 1  # Increment silence counter if speech had already started

                # Save the audio chunk only if speech has started
                if is_speaking:
                    audio_chunks.append(audio_chunk.copy())

            except Exception as cb_err:
                logger.error(f"Error during speech recording callback: {cb_err}")

        # Open the active input stream with a fixed block size for chunking
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=callback,
            dtype=np.int16,
            blocksize=chunk_size,
        ):
            start_time = time.time()
            while True:
                time.sleep(0.05)
                
                # Stop if no speech is detected at all within the initial 5 seconds
                if not is_speaking and (time.time() - start_time > 5.0):
                    logger.info("No speech detected, stopping recording.")
                    break
                
                # Stop if speech started and continuous silence limit has been reached
                if is_speaking and silent_chunks >= max_silent_chunks:
                    logger.info("Silence detected, stopping recording.")
                    break

        if not audio_chunks:
            return None

        # Concatenate all recorded chunks into a single NumPy array
        recorded_audio = np.concatenate(audio_chunks, axis=0)
        logger.info("Speech recording completed.")
        return recorded_audio

    except Exception as e:
        logger.error(f"Error recording speech dynamically: {e}")
        return None

def audio_to_wav_bytes(audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Converts a NumPy audio array into WAV-formatted bytes in memory."""
    wav_buffer = io.BytesIO()
    
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)      # 16-bit (2 bytes)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array.tobytes())
        
    wav_buffer.seek(0)
    return wav_buffer.read()