from typing import Dict, Tuple
from colorama import Fore, Back, Style
import json
import os

class ThemeManager:
    DEFAULT_THEMES = {
        "classic": {
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
        "neon": {
            "0": (Fore.BLACK, Back.BLACK),
            "2": (Fore.BLACK, Back.LIGHTCYAN_EX),
            "4": (Fore.BLACK, Back.LIGHTGREEN_EX),
            "8": (Fore.BLACK, Back.LIGHTRED_EX),
            "16": (Fore.BLACK, Back.LIGHTYELLOW_EX),
            "32": (Fore.BLACK, Back.LIGHTMAGENTA_EX),
            "64": (Fore.BLACK, Back.LIGHTBLUE_EX),
            "128": (Fore.WHITE, Back.CYAN),
            "256": (Fore.WHITE, Back.GREEN),
            "512": (Fore.WHITE, Back.RED),
            "1024": (Fore.WHITE, Back.YELLOW),
            "2048": (Fore.WHITE, Back.MAGENTA),
            "4096": (Fore.WHITE, Back.BLUE)
        },
        "monochrome": {
            "0": (Fore.BLACK, Back.BLACK),
            "2": (Fore.WHITE, Back.BLACK),
            "4": (Fore.LIGHTWHITE_EX, Back.BLACK),
            "8": (Fore.WHITE, Back.BLACK),
            "16": (Fore.LIGHTWHITE_EX, Back.BLACK),
            "32": (Fore.WHITE, Back.BLACK),
            "64": (Fore.LIGHTWHITE_EX, Back.BLACK),
            "128": (Fore.WHITE, Back.BLACK),
            "256": (Fore.LIGHTWHITE_EX, Back.BLACK),
            "512": (Fore.WHITE, Back.BLACK),
            "1024": (Fore.LIGHTWHITE_EX, Back.BLACK),
            "2048": (Fore.WHITE, Back.BLACK),
            "4096": (Fore.LIGHTWHITE_EX, Back.BLACK)
        },
        "ocean": {
            "0": (Fore.BLACK, Back.BLACK),
            "2": (Fore.WHITE, Back.BLUE),
            "4": (Fore.WHITE, Back.CYAN),
            "8": (Fore.WHITE, Back.LIGHTBLUE_EX),
            "16": (Fore.WHITE, Back.LIGHTCYAN_EX),
            "32": (Fore.BLACK, Back.BLUE),
            "64": (Fore.BLACK, Back.CYAN),
            "128": (Fore.BLACK, Back.LIGHTBLUE_EX),
            "256": (Fore.BLACK, Back.LIGHTCYAN_EX),
            "512": (Fore.WHITE, Back.BLUE),
            "1024": (Fore.WHITE, Back.CYAN),
            "2048": (Fore.WHITE, Back.LIGHTBLUE_EX),
            "4096": (Fore.WHITE, Back.LIGHTCYAN_EX)
        }
    }
    
    def __init__(self):
        self.themes_file = "themes.json"
        self.current_theme = "classic"
        self.themes = self.load_themes()
    
    def load_themes(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, 'r') as f:
                    themes_data = json.load(f)
                    themes = {}
                    for theme_name, theme_colors in themes_data.items():
                        themes[theme_name] = {
                            value: (getattr(Fore, fore.upper()), getattr(Back, back.upper()))
                            for value, (fore, back) in theme_colors.items()
                        }
                    return themes
            except:
                pass
        return self.DEFAULT_THEMES.copy()
    
    def save_themes(self) -> None:
        themes_data = {}
        for theme_name, theme_colors in self.themes.items():
            themes_data[theme_name] = {
                value: (fore.replace(Fore.PREFIX, '').lower(),
                       back.replace(Back.PREFIX, '').lower())
                for value, (fore, back) in theme_colors.items()
            }
        
        with open(self.themes_file, 'w') as f:
            json.dump(themes_data, f, indent=2)
    
    def get_current_theme(self) -> Dict[str, Tuple[str, str]]:
        return self.themes[self.current_theme]
    
    def set_theme(self, theme_name: str) -> bool:
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def add_custom_theme(self, name: str, colors: Dict[str, Tuple[str, str]]) -> bool:
        if name not in self.themes:
            self.themes[name] = colors
            self.save_themes()
            return True
        return False
    
    def get_available_themes(self) -> list:
        return list(self.themes.keys())
    
    def delete_theme(self, name: str) -> bool:

        if name in self.themes and name not in self.DEFAULT_THEMES:
            del self.themes[name]
            self.save_themes()
            return True
        return False 