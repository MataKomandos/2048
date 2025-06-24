import json
from typing import Dict, Any
from colorama import Fore, Back, Style

class Settings:
    """Class managing game settings and preferences."""
    
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
            "blue": {
                "0": (Fore.BLACK, Back.BLACK),
                "2": (Fore.WHITE, Back.BLUE),
                "4": (Fore.WHITE, Back.BLUE),
                "8": (Fore.WHITE, Back.BLUE),
                "16": (Fore.WHITE, Back.BLUE),
                "32": (Fore.WHITE, Back.BLUE),
                "64": (Fore.WHITE, Back.BLUE),
                "128": (Fore.WHITE, Back.BLUE),
                "256": (Fore.WHITE, Back.BLUE),
                "512": (Fore.WHITE, Back.BLUE),
                "1024": (Fore.WHITE, Back.BLUE),
                "2048": (Fore.WHITE, Back.BLUE),
                "4096": (Fore.WHITE, Back.BLUE)
            },
            "black": {
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
        """Initialize settings."""
        self.settings_file = "settings.json"
        from ui.theme_manager import ThemeManager
        self.theme_manager = ThemeManager()
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default."""
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                print(f"Wczytane ustawienia: {settings}")  # Debug
                
                # Sprawdź czy wybrany motyw istnieje w domyślnych motywach
                if settings.get("color_theme") not in self.DEFAULT_SETTINGS["themes"]:
                    print(f"Nieprawidłowy motyw: {settings.get('color_theme')}, ustawiam domyślny")  # Debug
                    settings["color_theme"] = "default"
                
                # Ensure all default settings exist
                for key, value in self.DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                    elif key == "themes":
                        settings[key] = self.DEFAULT_SETTINGS[key]
                
                print(f"Końcowe ustawienia: {settings}")  # Debug
                return settings
        except (FileNotFoundError, json.JSONDecodeError):
            print("Tworzę domyślne ustawienia")  # Debug
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self) -> None:
        """Save current settings to file."""
        # Stwórz kopię ustawień do zapisu
        settings_to_save = {
            "board_size": self.settings["board_size"],
            "target_value": self.settings["target_value"],
            "color_theme": self.settings["color_theme"]
        }
        
        # Nie zapisujemy motywów do pliku - zawsze używamy domyślnych
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
    
    def get_board_size(self) -> int:
        """Get current board size."""
        return self.settings["board_size"]
    
    def set_board_size(self, size: int) -> None:
        """Set board size."""
        if size in [3, 4, 5, 6]:
            self.settings["board_size"] = size
            self.save_settings()
    
    def get_target_value(self) -> int:
        """Get current target value."""
        return self.settings["target_value"]
    
    def set_target_value(self, value: int) -> None:
        """Set target value."""
        if value in [1024, 2048, 4096]:
            self.settings["target_value"] = value
            self.save_settings()
    
    def get_color_theme(self) -> str:
        """Get current color theme."""
        return self.settings["color_theme"]
    
    def set_color_theme(self, theme: str) -> None:
        """Set color theme."""
        print(f"Próba ustawienia motywu: {theme}")  # Debug
        available_themes = self.theme_manager.get_available_themes()
        print(f"Dostępne motywy: {available_themes}")  # Debug
        
        if theme in available_themes:
            print(f"Ustawiam motyw na: {theme}")  # Debug
            self.settings["color_theme"] = theme
            # Aktualizuj kolory motywu z ThemeManager
            self.settings["themes"][theme] = self.theme_manager.themes[theme]
            self.save_settings()
        else:
            print(f"Motyw {theme} nie istnieje!")  # Debug
    
    def get_theme_colors(self) -> Dict:
        """Pobierz kolory aktualnego motywu.
        
        Returns:
            Dict: Słownik z kolorami dla każdej wartości bloku
        """
        theme = self.get_color_theme()
        # Pobierz kolory z ThemeManager
        return self.theme_manager.themes[theme]
    
    def get_available_themes(self) -> list:
        """Get list of available themes."""
        return list(self.settings["themes"].keys()) 