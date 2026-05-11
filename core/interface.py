import customtkinter as ctk
from utils.logger import logger
import queue

class SpidyInterface:
    def __init__(self, message_queue: queue.Queue):
        logger.info("Initializing CustomTkinter Interface...")
        self.message_queue = message_queue
        
        self.app = ctk.CTk()
        self.app.title("Spidy Assistant")
        # Make the window float on top and remove title bar for a modern "pill" feel
        self.app.attributes("-topmost", True)
        self.app.overrideredirect(True)
        
        # Center the window at the top
        screen_width = self.app.winfo_screenwidth()
        x = (screen_width // 2) - (400 // 2)
        self.app.geometry(f"400x120+{x}+20")
        
        # UI Elements
        self.frame = ctk.CTkFrame(master=self.app, corner_radius=20, fg_color="#1F2937")
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.status_label = ctk.CTkLabel(
            master=self.frame, 
            text="Spidy is Sleeping", 
            font=("Roboto", 20, "bold"),
            text_color="#9CA3AF"
        )
        self.status_label.pack(pady=(15, 5))
        
        self.info_label = ctk.CTkLabel(
            master=self.frame,
            text="Waiting for 'Hey Jarvis'...",
            font=("Roboto", 14),
            text_color="#6B7280"
        )
        self.info_label.pack()
        
        # Setup polling for the queue on the main thread
        self.app.after(100, self.poll_queue)

    def poll_queue(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()
                if msg["type"] == "WAKE_WORD_DETECTED":
                    self.set_listening()
                elif msg["type"] == "PROCESSING":
                    self.set_processing()
                elif msg["type"] == "SPEAKING":
                    self.set_speaking(msg.get("text", ""))
                elif msg["type"] == "SLEEPING":
                    self.set_sleeping()
                elif msg["type"] == "EXIT":
                    self.app.quit()
        except queue.Empty:
            pass
        finally:
            self.app.after(100, self.poll_queue)
            
    def set_listening(self):
        self.status_label.configure(text="Listening...", text_color="#3B82F6")
        self.info_label.configure(text="I am ready for your command.", text_color="#E5E7EB")
        
    def set_processing(self):
        self.status_label.configure(text="Processing...", text_color="#F59E0B")
        self.info_label.configure(text="Understanding...", text_color="#E5E7EB")
        
    def set_speaking(self, text: str):
        self.status_label.configure(text="Speaking", text_color="#10B981")
        display_text = text if len(text) < 40 else text[:37] + "..."
        self.info_label.configure(text=display_text, text_color="#E5E7EB")
        
    def set_sleeping(self):
        self.status_label.configure(text="Spidy is Sleeping", text_color="#9CA3AF")
        self.info_label.configure(text="Waiting for 'Hey Jarvis'...", text_color="#6B7280")
        
    def run(self):
        logger.info("Starting main GUI loop.")
        self.app.mainloop()
