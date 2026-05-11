from utils.logger import logger
from utils.helpers import clean_text
import config
from faster_whisper import WhisperModel
import numpy as np

# Import skills here
from skills.web import WeatherSkill, WikipediaSkill
from skills.system import VolumeSkill, BrightnessSkill, SystemStateSkill
from skills.apps import AppLauncherSkill
from core.speaker import Speaker

class IntentProcessor:
    def __init__(self):
        logger.info("Initializing Intent Processor and registering skills...")
        self.speaker = Speaker()
        self.skills = [
            WeatherSkill(),
            WikipediaSkill(),
            VolumeSkill(),
            BrightnessSkill(),
            SystemStateSkill(),
            AppLauncherSkill()
        ]
        
        logger.info(f"Loading Whisper Model: {config.WHISPER_MODEL}")
        try:
            self.whisper_model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
        except Exception as e:
            logger.error(f"Failed to load Whisper Model: {e}")
            self.whisper_model = None
        
    def process_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribes audio using Whisper and processes text.
        Handles confidence thresholding.
        """
        if not self.whisper_model:
            logger.error("Whisper model not loaded.")
            msg = "Speech to text is unavailable."
            self.speaker.speak(msg)
            return msg
            
        try:
            # Faster whisper expects float32 between -1.0 and 1.0
            audio_float32 = audio_data.astype(np.float32) / 32768.0
            
            prompt = "Volume, Brightness, Chrome, YouTube, Screenshot"
            segments, info = self.whisper_model.transcribe(
                audio_float32, 
                beam_size=5,
                patience=1.0,
                initial_prompt=prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=800)
            )
            
            transcribed_text = ""
            low_confidence = False
            
            for segment in segments:
                # no_speech_prob > 0.7 means >= 30% confidence that speech happened
                if segment.no_speech_prob > (1.0 - config.WHISPER_CONFIDENCE_THRESHOLD):
                    low_confidence = True
                    continue
                transcribed_text += segment.text + " "
                
            transcribed_text = transcribed_text.strip()
            
            # Hallucination check
            if not transcribed_text or len(transcribed_text) < 3:
                logger.warning("Empty or hallucinated text detected. Exiting silently.")
                return ""
            
            if low_confidence:
                logger.warning("Low confidence text detected. Exiting silently.")
                return ""
                
            logger.info(f"Transcribed Text: '{transcribed_text}'")
            return self.process_text(transcribed_text)
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            self.speaker.speak("I had trouble understanding the audio.")
            return "I had trouble understanding the audio."

    def process_text(self, text: str) -> str:
        """
        Match the incoming text to a registered skill and execute it.
        """
        logger.info(f"Processing text: '{text}'")
        
        response_text = "I'm not sure how to help with that."
        
        # Simple rule-based intent matching
        for skill in self.skills:
            if skill.match(text):
                logger.info(f"Matched skill: {skill.name}")
                resp = skill.execute(text)
                if resp:
                    response_text = resp
                else:
                    response_text = "Task completed."
                break
                
        self.speaker.speak(response_text)
        return response_text
