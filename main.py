import queue
import threading
from core.interface import SpidyInterface
from core.listener import ListenerThread
from core.processor import IntentProcessor
from utils.logger import logger

class SpidyApp:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.processor = IntentProcessor()
        self.listener = ListenerThread(
            message_queue=self.message_queue,
            get_busy_state=lambda: self.is_busy,
            speaker=self.processor.speaker
        )
        self.interface = SpidyInterface(message_queue=self.message_queue)
        self.is_busy = False
        
        # We need a hook inside the UI loop to handle the WAKE_WORD_DETECTED event and trigger processing.
        # We keep the UI updates simple in SpidyInterface, but intercept messages here.
        
        def custom_poll():
            try:
                while True:
                    msg = self.message_queue.get_nowait()
                    msg_type = msg["type"]
                    
                    if msg_type == "WAKE_WORD_DETECTED":
                        if not self.is_busy:
                            self.is_busy = True
                            self.interface.set_state("LISTENING")
                            # Spawn background thread for recording and processing
                            threading.Thread(target=self.handle_command, daemon=True).start()
                        else:
                            logger.info("Wake word detected but system is busy. Ignoring.")
                        
                    elif msg_type == "PROCESSING":
                        self.interface.set_state("PROCESSING")
                    elif msg_type == "SPEAKING":
                        # Return to wide eyes (LISTENING state) while speaking
                        self.interface.set_state("LISTENING")
                    elif msg_type == "SLEEPING":
                        self.interface.set_state("OFF")
                    elif msg_type == "EXIT":
                        self.interface.app.quit()
            except queue.Empty:
                pass
            finally:
                self.interface.app.after(100, custom_poll)
                
        # Override the poll loop
        self.interface.poll_queue = custom_poll
        # Ensure it's scheduled once
        self.interface.app.after(100, custom_poll)
        
    def handle_command(self):
        """Runs in a separate thread so the GUI doesn't freeze"""
        try:
            # 1. Record Audio (VAD loop now handles the 5s timeout internally)
            audio_data = self.listener.record_command(seconds=10)
            
            # 2. Update UI to processing (Squinting)
            self.message_queue.put({"type": "PROCESSING"})
            
            # 3. Transcribe and Process
            response = self.processor.process_audio(audio_data)
            
            # 4. Update UI to speaking if we have a valid response
            if response:
                self.message_queue.put({"type": "SPEAKING", "text": response})
                # Dynamic delay approximation for TTS to finish speaking
                import time
                time.sleep(1 + len(response) / 15)
            else:
                # Siri Timeout departure logic
                logger.info("No command received. Playing departure phrase.")
                departure_phrase = "Going back to sleep."
                self.message_queue.put({"type": "SPEAKING", "text": departure_phrase})
                self.processor.speaker.speak(departure_phrase)
                
            # 5. Back to sleeping (OFF state)
            self.message_queue.put({"type": "SLEEPING"})
            
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            self.message_queue.put({"type": "SLEEPING"})
        finally:
            self.is_busy = False

    def run(self):
        # Start the listener thread
        self.listener.start()
        # Start GUI (Blocking)
        self.interface.run()
        # Stop listener when GUI closes
        self.listener.stop()

if __name__ == "__main__":
    app = SpidyApp()
    app.run()
