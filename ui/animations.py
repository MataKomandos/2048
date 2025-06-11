from colorama import Fore, Back, Style
import time
import sys
import random

class Animations:
    @staticmethod
    def animate_merge(value: int) -> None:
        frames = [
            "╔═══╗",
            "║   ║",
            "╚═══╝"
        ]
        
        for _ in range(2):
            for frame in frames:
                sys.stdout.write(f"\r{Fore.YELLOW}{frame}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(0.05)
        sys.stdout.write("\r     \r")
    
    @staticmethod
    def animate_new_tile(value: int) -> None:
        frames = ["·", "○", "◎", "●"]
        for frame in frames:
            sys.stdout.write(f"\r{Fore.CYAN}{frame}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write("\r \r")
    
    @staticmethod
    def celebrate_milestone(value: int) -> None:
        if value not in [512, 1024, 2048]:
            return
            
        colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
        celebration = {
            512: "★ Wspaniale! 512! ★",
            1024: "✨ Niesamowite! 1024! ✨",
            2048: "🌟 GRATULACJE! 2048! 🌟"
        }
        
        message = celebration[value]
        print("\n")
        for _ in range(3):
            for color in colors:
                sys.stdout.write(f"\r{color}{message}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(0.1)
        print("\n")
    
    @staticmethod
    def flash_color(text: str, color: str) -> None:
        for _ in range(3):
            sys.stdout.write(f"\r{color}{text}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write(f"\r{' ' * len(text)}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f"\r{color}{text}{Style.RESET_ALL}\n") 