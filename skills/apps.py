import os
import shutil
import winreg
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
        
        # Tier 1: Protocols (UWP)
        uwp_apps = {
            "camera": "microsoft.windows.camera:",
            "calculator": "calculator:",
            "settings": "ms-settings:",
            "mail": "outlookmail:",
            "maps": "bingmaps:",
            "calendar": "outlookcal:"
        }
        
        if app_name in uwp_apps:
            try:
                os.startfile(uwp_apps[app_name])
                return f"Opening {app_name}."
            except Exception as e:
                logger.error(f"Failed to launch UWP app {app_name}: {e}")
                
        # Tier 2: System PATH
        app_path = shutil.which(app_name)
        if app_path:
            try:
                subprocess.Popen(app_path)
                return f"Opening {app_name}."
            except Exception as e:
                logger.error(f"Failed to launch {app_name} from PATH: {e}")
                
        # Tier 3: Registry Lookup
        try:
            key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{app_name}.exe"
            try:
                # Check HKLM
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    target_path, _ = winreg.QueryValueEx(key, "")
            except FileNotFoundError:
                # Fallback to HKCU
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    target_path, _ = winreg.QueryValueEx(key, "")
                    
            if target_path:
                # Remove quotes if present
                target_path = target_path.strip('"')
                subprocess.Popen(target_path)
                return f"Opening {app_name}."
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Failed to launch {app_name} from Registry: {e}")
            
        return f"I couldn't find an application named {app_name} on this system."
