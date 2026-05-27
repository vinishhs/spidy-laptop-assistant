import customtkinter as ctk
from PIL import Image
import os
import random
from utils.logger import logger
import queue

class SpidyInterface:
    def __init__(self, message_queue: queue.Queue):
        logger.info("Initializing Animated Spidy UI...")
        self.message_queue = message_queue
        
        self.app = ctk.CTk()
        
        # Window setup: Borderless, Topmost, Transparent
        self.app.overrideredirect(True)
        self.app.attributes("-topmost", True)
        
        # Pro-Tip logic: Use #010101 for better anti-aliasing transparency
        self.app.attributes("-transparentcolor", "#010101")
        self.app.configure(fg_color="#010101")
        
        # 100x100 window positioned at bottom center (just above taskbar)
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        window_width = 100
        window_height = 100
        center_x = int((screen_width / 2) - (window_width / 2))
        bottom_y = int(screen_height - (window_height + 60))
        self.app.geometry(f"100x100+{center_x}+{bottom_y}")

        # Load assets (relative to core/)
        assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        try:
            self.img_open = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_path, "spidy_open.png")),
                size=(100, 100)
            )
            self.img_half = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_path, "spidy_half.png")),
                size=(100, 100)
            )
        except Exception as e:
            logger.error(f"Failed to load UI assets: {e}")
            # Fallback (empty images or similar would go here)

        self.image_label = ctk.CTkLabel(self.app, image=self.img_open, text="", fg_color="#010101")
        self.image_label.pack(expand=True, fill="both")

        self.is_blinking = False
        self.blink_id = None
        
        # Hide initially (Dormant state)
        self.app.withdraw()
        
        # Internal poll loop placeholder (overridden by main.py)
        self.app.after(100, self.poll_queue)

    def set_state(self, state: str):
        """
        Transition Spidy between states: OFF, LISTENING, PROCESSING.
        """
        logger.info(f"UI State Transition: {state}")
        
        if state == "OFF":
            self.stop_blink()
            self.app.withdraw()
        elif state == "LISTENING":
            self.image_label.configure(image=self.img_open)
            self.app.deiconify()
            self.start_blink()
        elif state == "PROCESSING":
            self.stop_blink()
            # Squinting eyes signal thinking
            self.image_label.configure(image=self.img_half)
            self.app.deiconify()

    def start_blink(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.blink()

    def stop_blink(self):
        self.is_blinking = False
        if self.blink_id:
            self.app.after_cancel(self.blink_id)
            self.blink_id = None

    def blink(self):
        """Non-blocking blink logic."""
        if not self.is_blinking:
            return
        
        # Switch to half-closed eyes
        self.image_label.configure(image=self.img_half)
        
        # Return to wide eyes after 150ms
        self.app.after(150, lambda: self.image_label.configure(image=self.img_open))
        
        # Schedule next blink at random interval (2-6 seconds)
        next_blink = random.randint(2000, 6000)
        self.blink_id = self.app.after(next_blink, self.blink)

    def poll_queue(self):
        """Placeholder for message queue polling logic."""
        # Note: In main.py, this is overridden by a custom poll loop
        self.app.after(100, self.poll_queue)

    def run(self):
        logger.info("Starting Spidy UI mainloop.")
        self.app.mainloop()
