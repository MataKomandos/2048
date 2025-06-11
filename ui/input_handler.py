import msvcrt
import sys
from typing import Optional

class InputHandler:
    ENTER_KEY = b'\r'
    BACKSPACE_KEY = b'\x08'
    ESC_KEY = b'\x1b'
    ARROW_PREFIX = b'\xe0'
    
    ARROW_UP = b'H'
    ARROW_DOWN = b'P'
    ARROW_LEFT = b'K'
    ARROW_RIGHT = b'M'
    
    REGULAR_KEY_MAPPING = {
        b'q': 'quit',
        b'Q': 'quit',
        b'r': 'restart',
        b'R': 'restart',
        b'h': 'help',
        b'H': 'help',
        b'z': 'undo',
        b'Z': 'undo',
    }
    
    SPECIAL_KEY_MAPPING = {
        ARROW_UP: 'up',
        ARROW_DOWN: 'down',
        ARROW_LEFT: 'left',
        ARROW_RIGHT: 'right',
    }
    
    @staticmethod
    def get_input() -> Optional[str]:
        if sys.platform == 'win32':
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == InputHandler.ARROW_PREFIX:
                    key = msvcrt.getch()
                    return InputHandler.SPECIAL_KEY_MAPPING.get(key, '')
                else:
                    return InputHandler.REGULAR_KEY_MAPPING.get(key, '')
        else:
            key = sys.stdin.read(1)
            if key == '\x1b':
                key = sys.stdin.read(1)
                if key == 'A': return 'up'
                if key == 'B': return 'down'
                if key == 'C': return 'right'
                if key == 'D': return 'left'
            return InputHandler.REGULAR_KEY_MAPPING.get(key.encode(), '')
        return None
    
    @staticmethod
    def get_menu_input() -> int:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    num = int(key.decode('ascii'))
                    print(num)
                    return num
                except (ValueError, UnicodeDecodeError):
                    pass
    
    @staticmethod
    def get_number_input(min_value: int, max_value: int) -> int:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    num = int(key.decode('ascii'))
                    if min_value <= num <= max_value:
                        print(num)
                        return num
                except (ValueError, UnicodeDecodeError):
                    pass
    
    @staticmethod
    def get_text_input(allow_empty: bool = False) -> str:
        text = ""
        while True:
            key = msvcrt.getch()
            
            if key == InputHandler.ENTER_KEY:
                print()
                if text or allow_empty:
                    return text
                continue
            
            if key == InputHandler.BACKSPACE_KEY:
                if text:
                    text = text[:-1]
                    print('\b \b', end='', flush=True)
                continue
            
            try:
                char = key.decode('ascii')
                if char.isalnum() or char == '_':
                    text += char
                    print(char, end='', flush=True)
            except UnicodeDecodeError:
                pass
    
    @staticmethod
    def wait_key() -> None:
        msvcrt.getch() 