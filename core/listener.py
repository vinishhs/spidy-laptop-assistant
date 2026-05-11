import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
from utils.logger import logger
import queue
import threading
import time

# Pre-download models to cache
openwakeword.utils.download_models()

class ListenerThread:
    """
    Runs an openWakeWord detection loop in a background thread.
    Communicates with the main GUI thread via queue.Queue.
    """
    def __init__(self, message_queue: queue.Queue, wake_word_model: str = "hey_jarvis"):
        self.message_queue = message_queue
        self.wake_word_model = wake_word_model
        
        logger.info(f"Initializing Wake Word Model: {wake_word_model}")
        try:
            self.model = Model(wakeword_models=[wake_word_model], inference_framework="onnx")
        except Exception as e:
            logger.error(f"Failed to load OpenWakeWord model: {e}")
            self.model = None

        self.mic = None
        self.stream = None
        self.running = False
        
    def start(self):
        if not self.model:
            return
            
        self.running = True
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(format=pyaudio.paInt16,
                                    channels=1,
                                    rate=16000,
                                    input=True,
                                    frames_per_buffer=1280)
                                    
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("Background listener thread started.")
        
    def _listen_loop(self):
        logger.info("Listening for wake word...")
        while self.running:
            try:
                data = np.frombuffer(self.stream.read(1280, exception_on_overflow=False), dtype=np.int16)
                prediction = self.model.predict(data)
                
                for model_name, score in prediction.items():
                    if score > 0.5:
                        logger.info(f"Wake word detected! Model: {model_name}, Score: {score}")
                        self.message_queue.put({"type": "WAKE_WORD_DETECTED", "score": score})
                        
                        # Wait a bit after detection to prevent spamming
                        time.sleep(1.5)
                        # We won't listen for wake word immediately while processing command
                        
            except Exception as e:
                logger.error(f"Audio stream error: {e}")
                self.running = False

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
            
    def record_command(self, seconds=10, silence_threshold=0.8) -> np.ndarray:
        """
        Records audio dynamically until a sustained period of silence (VAD).
        Returns the audio buffer as a numpy array.
        """
        if not self.stream:
            return np.array([])
            
        logger.info(f"Recording command dynamically...")
        frames = []
        
        # rate/chunk = 16000/1280 = 12.5 chunks per sec
        max_silence_chunks = int(silence_threshold * 12.5)
        # Maximum allowed chunks
        max_chunks = int(seconds * 12.5)
        silence_count = 0
        is_speaking = False
        
        # Clear trailing audio from the initial trigger
        for _ in range(2):
            self.stream.read(1280, exception_on_overflow=False)
            
        # Hard cap based on seconds param
        for _ in range(max_chunks):
            data = self.stream.read(1280, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))
            
            # Simple Numpy RMS Check
            chunk_array = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(np.square(chunk_array, dtype=np.float64)))
            
            if rms > 500: # Threshold floor
                is_speaking = True
                silence_count = 0
            elif is_speaking:
                silence_count += 1
                
            if is_speaking and silence_count > max_silence_chunks:
                logger.info("Silence detected. Stopping recording immediately.")
                break
            
        logger.info("Recording finished. Applying noise reduction...")
        audio_array = np.concatenate(frames)
        
        try:
            import noisereduce as nr
            # Apply noisereduce on the raw int16 array
            reduced_audio = nr.reduce_noise(y=audio_array, sr=16000, prop_decrease=0.8)
            return reduced_audio
        except Exception as e:
            logger.warning(f"Noise reduction skipped: {e}")
            return audio_array
