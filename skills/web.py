from skills.base import BaseSkill
from utils.logger import logger
from utils.helpers import clean_text
import config

class WeatherSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "WeatherSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["weather", "temperature", "how hot", "how cold"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing WeatherSkill for command: {command}")
        
        if config.USE_MOCK_WEATHER:
            return "The simulated weather is 24 degrees Celsius and sunny."
            
        # In the future, parse location from command and call OpenWeatherMap
        return "Real weather fetching is not integrated yet."


class WikipediaSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "WikipediaSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["wikipedia", "who is", "what is", "tell me about"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing WikipediaSkill for command: {command}")
        cleaned = clean_text(command)
        
        # Remove trigger words
        query = command.lower()
        for intent in self.intents:
            query = query.replace(intent, "")
        query = query.strip()
        
        if not query:
            return "What would you like me to look up on Wikipedia?"
            
        try:
            import wikipedia
            wikipedia.set_lang("en")
            # Ask for 2 sentences as per PRD
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except Exception as e:
            logger.error(f"Wikipedia lookup failed: {e}")
            return f"I couldn't find any information on {query}."
