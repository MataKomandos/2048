from typing import Optional
from colorama import Fore, Back, Style
import time
import random

from core.board import Board
from core.player import Player
from core.settings import Settings
from ui.display import Display
from ui.input_handler import InputHandler
from .ai_assistant import AI2048
from core.error_handler import ErrorHandler
from core.database_manager import DatabaseManager

class ClassicAIMode:
    
    def __init__(self):
        self.board = None
        self.player = None
        self.ai = None
        self.moves = 0
        self.needs_redraw = True
        self.running = True
        self.error_handler = ErrorHandler()
        self.db_manager = DatabaseManager()
        self.db_player = None
        self.db_game = None
    
    def get_theme_colors(self) -> dict:
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
    
    def setup_game(self, player: Player) -> None:
        
        Display.clear_screen()
        print(f"\n{Fore.CYAN}=== TRYB KLASYCZNY Z ASYSTENTEM AI ==={Style.RESET_ALL}")
        print("\nWybierz poziom trudności:")
        print("1. Łatwy (10 podpowiedzi, 10% szans na '4')")
        print("2. Normalny (5 podpowiedzi, 20% szans na '4')")
        print("3. Trudny (3 podpowiedzi, 30% szans na '4')")
        
        while True:
            choice = InputHandler.get_menu_input()
            if choice in [1, 2, 3]:
                difficulty = {1: "łatwy", 2: "normalny", 3: "trudny"}[choice]
                break
            print("\nNieprawidłowy wybór. Spróbuj ponownie.")
        
        self.player = player
        self.board = Board()
        self.ai = AI2048(difficulty)
        
        print(f"\nWybrano poziom: {difficulty}")
        print(f"Dostępne podpowiedzi: {self.ai.hints_left}")
        print("\nNaciśnij dowolny klawisz, aby rozpocząć...")
        InputHandler.wait_key()
    
    def display_game_state(self) -> None:
        
        if not self.needs_redraw:
            return
            
        Display.clear_screen()
        Display.display_board(
            self.board.get_board(),
            self.board.get_score(),
            self.player.nickname,
            self.get_theme_colors(),
            None,
            True,
            self.ai.hints_left
        )
        
        print(f"\n{Fore.YELLOW}=== ASYSTENT AI ==={Style.RESET_ALL}")
        print(f"Pozostałe podpowiedzi: {self.ai.hints_left}")
        print(f"Poziom trudności: {self.ai.difficulty}")
        print(f"Wykonane ruchy: {self.moves}")
        print("\nH = Podpowiedź, Q = Wyjście")
        
        self.needs_redraw = False
    
    def process_input(self) -> bool:
        
        command = InputHandler.get_input()
        if not command:
            return True
        
        if command == 'quit':
            return False
        
        if command == 'help':
            if self.ai.hints_left > 0:
                suggested_move = self.ai.suggest_move(self.board.get_board())
                if suggested_move:
                    self.needs_redraw = True
                    Display.clear_screen()
                    self.display_game_state()
                    print(f"\n{Fore.GREEN}Sugerowany ruch: {suggested_move}{Style.RESET_ALL}")
                    time.sleep(1.5)
                    self.needs_redraw = True
            else:
                self.needs_redraw = True
                Display.clear_screen()
                self.display_game_state()
                print(f"\n{Fore.RED}Brak dostępnych podpowiedzi!{Style.RESET_ALL}")
                time.sleep(1.5)
                self.needs_redraw = True
            return True
        
        if command in ['up', 'down', 'left', 'right']:
            if self.board.move(command):
                self.moves += 1
                self.needs_redraw = True
                
                new_number = self.ai.get_next_number()
                self._add_new_tile(new_number)
                
                game_over, status = self.ai.check_game_over(
                    self.board.get_board(),
                    self.board.settings.get_target_value()
                )
                
                if game_over:
                    self.handle_game_over(status)
                    return False
                
                self.ai.adjust_difficulty(
                    self.board.get_score(),
                    self.moves,
                    status == "victory"
                )
        
        return True
    
    def _add_new_tile(self, value: int) -> None:
        
        empty_cells = [
            (i, j) for i in range(self.board.size)
            for j in range(self.board.size)
            if self.board.board[i][j] == 0
        ]
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board.board[i][j] = value
    
    def handle_game_over(self, status: str) -> None:
        
        Display.clear_screen()
        Display.display_board(
            self.board.get_board(),
            self.board.get_score(),
            self.player.nickname,
            self.get_theme_colors(),
            None,
            False,
            0
        )
        
        if status == "victory":
            print(f"\n{Fore.GREEN}Gratulacje! Osiągnąłeś cel!{Style.RESET_ALL}")
        elif status == "impossible":
            print(f"\n{Fore.RED}Nie ma już możliwości osiągnięcia celu.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}Koniec gry!{Style.RESET_ALL}")
        
        print(f"\nWynik końcowy: {self.board.get_score()}")
        print(f"Liczba ruchów: {self.moves}")
        print(f"Największy blok: {max(max(row) for row in self.board.get_board())}")
        
        self.player.save_score(self.board.get_score())
        InputHandler.wait_key()
    
    def run(self, player: Player) -> None:
        
        self.setup_game(player)
        self.needs_redraw = True
        
        while self.running:
            self.display_game_state()
            if not self.process_input():
                break
            time.sleep(0.05)