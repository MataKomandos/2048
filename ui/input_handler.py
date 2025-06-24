import msvcrt
import sys
from typing import Optional

class InputHandler:
    """Klasa obsługująca wprowadzanie danych przez użytkownika."""
    
    # Kody klawiszy specjalnych
    ENTER_KEY = b'\r'
    BACKSPACE_KEY = b'\x08'
    ESC_KEY = b'\x1b'
    ARROW_PREFIX = b'\xe0'
    
    # Kody klawiszy strzałek ASCII
    ARROW_UP = b'H'
    ARROW_DOWN = b'P'
    ARROW_LEFT = b'K'
    ARROW_RIGHT = b'M'
    
    # Regular key mappings (for non-special keys)
    REGULAR_KEY_MAPPING = {
        b'q': 'quit',   # Q key
        b'Q': 'quit',   # Q key (caps)
        b'r': 'restart', # R key
        b'R': 'restart', # R key (caps)
        b'h': 'help',   # H key
        b'H': 'help',   # H key (caps)
        b'z': 'undo',   # Z key
        b'Z': 'undo',   # Z key (caps)
    }
    
    # Special key mappings (for keys after SPECIAL_KEY)
    SPECIAL_KEY_MAPPING = {
        ARROW_UP: 'up',
        ARROW_DOWN: 'down',
        ARROW_LEFT: 'left',
        ARROW_RIGHT: 'right',
    }
    
    @staticmethod
    def get_input() -> Optional[str]:
        """Get and process user input.
        
        Returns:
            Optional[str]: The processed input command or None if invalid
        """
        if sys.platform == 'win32':
            # Windows input handling
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == InputHandler.ARROW_PREFIX:
                    # Handle special keys (arrows)
                    key = msvcrt.getch()
                    return InputHandler.SPECIAL_KEY_MAPPING.get(key, '')
                else:
                    # Handle regular keys
                    return InputHandler.REGULAR_KEY_MAPPING.get(key, '')
        else:
            # Unix-like systems input handling
            key = sys.stdin.read(1)
            if key == '\x1b':  # Escape sequence
                sys.stdin.read(1)  # Skip [
                key = sys.stdin.read(1)
                if key == 'W': return 'up'
                if key == 'S': return 'down'
                if key == 'D': return 'right'
                if key == 'A': return 'left'
            return InputHandler.REGULAR_KEY_MAPPING.get(key.encode(), '')
        return None
    
    @staticmethod
    def get_menu_input() -> int:
        """Pobiera wybór opcji z menu.
        
        Returns:
            int: Numer wybranej opcji
        """
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    num = int(key.decode('ascii'))
                    print(num)  # Echo wprowadzonej liczby
                    return num
                except (ValueError, UnicodeDecodeError):
                    pass
    
    @staticmethod
    def get_number_input(min_value: int, max_value: int) -> int:
        """Pobiera liczbę z określonego zakresu.
        
        Args:
            min_value (int): Minimalna dozwolona wartość
            max_value (int): Maksymalna dozwolona wartość
            
        Returns:
            int: Wybrana liczba z zakresu
        """
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    num = int(key.decode('ascii'))
                    if min_value <= num <= max_value:
                        print(num)  # Echo wprowadzonej liczby
                        return num
                except (ValueError, UnicodeDecodeError):
                    pass
    
    @staticmethod
    def get_text_input(allow_empty: bool = False) -> str:
        """Pobiera tekst od użytkownika (np. nick).
        
        Args:
            allow_empty (bool): Czy dozwolone jest puste pole
            
        Returns:
            str: Wprowadzony tekst
        """
        text = ""
        while True:
            key = msvcrt.getch()
            
            # Obsługa klawisza Enter
            if key == InputHandler.ENTER_KEY:
                print()  # Przejdź do następnej linii
                if text or allow_empty:  # Akceptuj tylko niepusty tekst (chyba że allow_empty=True)
                    return text
                continue
            
            # Obsługa klawisza Backspace
            if key == InputHandler.BACKSPACE_KEY:
                if text:
                    text = text[:-1]
                    # Usuń ostatni znak z ekranu
                    print('\b \b', end='', flush=True)
                continue
            
            # Obsługa zwykłych znaków
            try:
                char = key.decode('ascii')
                # Akceptuj tylko znaki alfanumeryczne i podkreślenie
                if char.isalnum() or char == '_':
                    text += char
                    print(char, end='', flush=True)
            except UnicodeDecodeError:
                pass
    
    @staticmethod
    def wait_key() -> None:
        """Czeka na naciśnięcie dowolnego klawisza."""
        msvcrt.getch() 