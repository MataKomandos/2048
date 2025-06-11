import json
from typing import Dict, Any
from colorama import Fore, Back, Style

class Settings:
    
    DEFAULT_SETTINGS = {
        "board_size": 4,
        "target_value": 2048,
        "color_theme": "default",
        "themes": {
            "default": {
                "0": (Fore.BLACK, Back.BLACK),
                "2": (Fore.BLACK, Back.WHITE),
                "4": (Fore.BLACK, Back.CYAN),
                "8": (Fore.BLACK, Back.GREEN),
                "16": (Fore.BLACK, Back.YELLOW),
                "32": (Fore.BLACK, Back.RED),
                "64": (Fore.WHITE, Back.BLUE),
                "128": (Fore.WHITE, Back.MAGENTA),
                "256": (Fore.BLACK, Back.LIGHTCYAN_EX),
                "512": (Fore.BLACK, Back.LIGHTGREEN_EX),
                "1024": (Fore.BLACK, Back.LIGHTYELLOW_EX),
                "2048": (Fore.BLACK, Back.LIGHTRED_EX),
                "4096": (Fore.WHITE, Back.LIGHTMAGENTA_EX)
            },
            "monochrome": {
                "0": (Fore.BLACK, Back.BLACK),
                "2": (Fore.WHITE, Back.BLACK),
                "4": (Fore.WHITE, Back.BLACK),
                "8": (Fore.WHITE, Back.BLACK),
                "16": (Fore.WHITE, Back.BLACK),
                "32": (Fore.WHITE, Back.BLACK),
                "64": (Fore.WHITE, Back.BLACK),
                "128": (Fore.WHITE, Back.BLACK),
                "256": (Fore.WHITE, Back.BLACK),
                "512": (Fore.WHITE, Back.BLACK),
                "1024": (Fore.WHITE, Back.BLACK),
                "2048": (Fore.WHITE, Back.BLACK),
                "4096": (Fore.WHITE, Back.BLACK)
            },
            "dark": {
                "0": (Fore.BLACK, Back.BLACK),
                "2": (Fore.GREEN, Back.BLACK),
                "4": (Fore.CYAN, Back.BLACK),
                "8": (Fore.BLUE, Back.BLACK),
                "16": (Fore.MAGENTA, Back.BLACK),
                "32": (Fore.RED, Back.BLACK),
                "64": (Fore.YELLOW, Back.BLACK),
                "128": (Fore.WHITE, Back.BLACK),
                "256": (Fore.LIGHTGREEN_EX, Back.BLACK),
                "512": (Fore.LIGHTCYAN_EX, Back.BLACK),
                "1024": (Fore.LIGHTBLUE_EX, Back.BLACK),
                "2048": (Fore.LIGHTMAGENTA_EX, Back.BLACK),
                "4096": (Fore.LIGHTRED_EX, Back.BLACK)
            }
        }
    }
    
    def __init__(self):
        self.settings_file = "settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                for key, value in self.DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> None:
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def get_board_size(self) -> int:
        return self.settings["board_size"]
    
    def set_board_size(self, size: int) -> None:
        if size in [3, 4, 5, 6]:
            self.settings["board_size"] = size
            self.save_settings()
    
    def get_target_value(self) -> int:
        return self.settings["target_value"]
    
    def set_target_value(self, value: int) -> None:
        if value in [1024, 2048, 4096]:
            self.settings["target_value"] = value
            self.save_settings()
    
    def get_color_theme(self) -> str:
        return self.settings["color_theme"]
    
    def set_color_theme(self, theme: str) -> None:      
        if theme in self.settings["themes"]:
            self.settings["color_theme"] = theme
            self.save_settings()
    
    def get_theme_colors(self) -> Dict:
        
        theme = self.get_color_theme()
        if not hasattr(self, 'theme_manager'):
            from ui.theme_manager import ThemeManager
            self.theme_manager = ThemeManager()
        
        return self.theme_manager.themes.get(theme, self.theme_manager.DEFAULT_THEMES['classic'])
    
    def get_available_themes(self) -> list:
        
        return list(self.settings["themes"].keys()) 