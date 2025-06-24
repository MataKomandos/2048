from typing import Dict, Tuple
from colorama import Fore, Back, Style
import json
import os

class ThemeManager:
    """Zarządca motywów kolorystycznych gry."""
    
    DEFAULT_THEMES = {
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
    
    def __init__(self):
        """Inicjalizacja menedżera motywów."""
        self.themes_file = "themes.json"
        self.current_theme = "classic"
        self.themes = self.load_themes()
    
    def load_themes(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        """Wczytaj motywy z pliku lub użyj domyślnych."""
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, 'r') as f:
                    themes_data = json.load(f)
                    # Konwertuj zapisane kody ANSI na obiekty Fore/Back
                    themes = {}
                    for theme_name, theme_colors in themes_data.items():
                        themes[theme_name] = {}
                        for value, (fore, back) in theme_colors.items():
                            # Konwertuj kody na obiekty colorama
                            fore_color = f"\033[{fore}m"
                            back_color = f"\033[{back}m"
                            themes[theme_name][value] = (fore_color, back_color)
                    return themes
            except Exception as e:
                print(f"Błąd wczytywania motywów: {e}")
                return self.DEFAULT_THEMES.copy()
        return self.DEFAULT_THEMES.copy()
    
    def save_themes(self) -> None:
        """Zapisz motywy do pliku."""
        # Konwertuj obiekty Fore/Back na nazwy kolorów
        themes_data = {}
        for theme_name, theme_colors in self.themes.items():
            themes_data[theme_name] = {
                value: (str(fore).replace('\033[', '').replace('m', ''),
                       str(back).replace('\033[', '').replace('m', ''))
                for value, (fore, back) in theme_colors.items()
            }
        
        with open(self.themes_file, 'w') as f:
            json.dump(themes_data, f, indent=2)
    
    def get_current_theme(self) -> Dict[str, Tuple[str, str]]:
        """Pobierz aktualny motyw."""
        return self.themes[self.current_theme]
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Ustaw aktywny motyw.
        
        Args:
            theme_name (str): Nazwa motywu
            
        Returns:
            bool: Czy udało się ustawić motyw
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def add_custom_theme(self, name: str, colors: Dict[str, Tuple[str, str]]) -> bool:
        """
        Dodaj nowy motyw użytkownika.
        
        Args:
            name (str): Nazwa motywu
            colors (Dict[str, Tuple[str, str]]): Definicje kolorów
            
        Returns:
            bool: Czy udało się dodać motyw
        """
        if name not in self.themes:
            self.themes[name] = colors
            self.current_theme = name  # Ustaw nowy motyw jako aktualny
            self.save_themes()
            return True
        return False
    
    def get_available_themes(self) -> list:
        """Pobierz listę dostępnych motywów."""
        return list(self.themes.keys())
    
    def delete_theme(self, name: str) -> bool:
        """
        Usuń motyw.
        
        Args:
            name (str): Nazwa motywu do usunięcia
            
        Returns:
            bool: Czy udało się usunąć motyw
        """
        if name in self.themes and name not in self.DEFAULT_THEMES:
            del self.themes[name]
            self.save_themes()
            return True
        return False 