import pyttsx3
from utils.logger import logger

class Speaker:
    def __init__(self):
        # We delay initialization to the threads to prevent Windows COM cross-thread errors
        self.rate = 170
        logger.info("Speaker configured for thread-safe cross-execution.")

    def speak(self, text: str):
        if not text:
            return

        logger.info(f"Speaking: '{text}'")
        try:
            # Re-init locally for the active thread to prevent UI lockup
            import pythoncom
            pythoncom.CoInitialize()
            
            engine = pyttsx3.init()
            # Windows defaults to SAPI5
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            
            engine.setProperty('rate', self.rate)
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            pass
        except Exception as e:
            logger.error(f"TTS Engine execution failed: {e}")
