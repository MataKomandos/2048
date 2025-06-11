from colorama import Fore, Back, Style
from core.settings import Settings

def get_theme_colors():
    """
    Pobiera kolory z aktualnego motywu.
    
    Returns:
        dict: Słownik z kolorami dla poszczególnych wartości kafelków
    """
    settings = Settings()
    return settings.get_theme_colors()

def get_theme_colors_old() -> dict:
    """
    Zwraca standardowy zestaw kolorów dla bloków w grze 2048.
    
    Returns:
        dict: Słownik mapujący wartości bloków na kolory (foreground, background)
    """
    return {
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
    } 