from skills.base import BaseSkill
from utils.logger import logger
from utils.helpers import parse_percentage
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import os

class VolumeSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "VolumeSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["volume"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing VolumeSkill for command: {command}")
        level = parse_percentage(command)
        
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            # SetMasterVolumeLevelScalar takes a float between 0.0 and 1.0
            scalar_level = level / 100.0
            volume.SetMasterVolumeLevelScalar(scalar_level, None)
            
            return f"Volume set to {level} percent."
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return "I encountered an error setting the volume."

class BrightnessSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "BrightnessSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["brightness", "screen"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing BrightnessSkill for command: {command}")
        level = parse_percentage(command)
        
        try:
            sbc.set_brightness(level)
            return f"Brightness set to {level} percent."
        except Exception as e:
            logger.error(f"Failed to set brightness: {e}")
            return "I encountered an error setting the brightness."

class SystemStateSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "SystemStateSkill"
        
    @property
    def intents(self) -> list[str]:
        return ["sleep", "lock", "shut down"]
        
    def execute(self, command: str) -> str:
        logger.info(f"Executing SystemStateSkill for command: {command}")
        cmd_lower = command.lower()
        if "sleep" in cmd_lower:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Going to sleep."
        elif "lock" in cmd_lower:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "System locked."
        elif "shut down" in cmd_lower:
            # Maybe add actual shut down or a warning
            return "I will not actually shut down your system yet for safety."
            
        return "I didn't understand the system command."
