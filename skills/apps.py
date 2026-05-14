from skills.base import BaseSkill
from utils.logger import logger
import subprocess
from utils.helpers import clean_text

class AppLauncherSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "AppLauncherSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["open", "launch", "start"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing AppLauncherSkill for command: {command}")
        cleaned = clean_text(command)
        
        query = command.lower().strip()
        for intent in self.intents:
            # Ensure intent is also standardized just in case
            query = query.replace(intent.lower().strip(), "")
        app_name = query.strip()
        
        try:
            # On Windows, using the start command is the easiest way to launch default apps
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Opening {app_name}."
        except Exception as e:
            logger.error(f"Failed to launch app: {e}")
            return f"I couldn't open {app_name}."
