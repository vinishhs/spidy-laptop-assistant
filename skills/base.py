from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.logger import logger

class BaseSkill(ABC):
    """
    Abstract Base Class for all Spidy Skills.
    Each skill must define intents it can handle and an execution method.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the skill."""
        pass
        
    @property
    @abstractmethod
    def intents(self) -> list[str]:
        """A list of keywords or phrases that trigger this skill."""
        pass

    @abstractmethod
    def execute(self, command: str) -> Optional[str]:
        """
        Executes the skill logic based on the user's command.
        Returns a string containing the text to be spoken by TTS, if applicable.
        """
        pass
        
    def match(self, command: str) -> bool:
        """Checks if the command matches any intent."""
        from utils.helpers import clean_text, fuzzy_match
        cleaned = clean_text(command)
        for intent in self.intents:
            if fuzzy_match(clean_text(intent), cleaned):
                return True
        return False
