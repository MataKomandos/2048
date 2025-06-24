from typing import Optional, Tuple
from core.board import Board
from core.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
from colorama import Fore, Style
import time
from .theme_colors import get_theme_colors
from core.error_handler import ErrorHandler
from core.database_manager import DatabaseManager

class TwoPlayerMode:
    """Tryb gry dla dwóch graczy (naprzemienne ruchy)."""
    
    def __init__(self):
        """Inicjalizacja trybu dla dwóch graczy."""
        self.board = None  # Wspólna plansza dla obu graczy
        self.player1 = None
        self.player2 = None
        self.current_player = 0  # 0 dla gracza 1, 1 dla gracza 2
        self.moves = [0, 0]  # Licznik ruchów dla każdego gracza
        self.needs_redraw = True
        self.running = True
        self.error_handler = ErrorHandler()
        self.db_manager = DatabaseManager()
        self.db_player1 = None
        self.db_player2 = None
        self.db_game = None

    def setup_game(self, player1: Player, player2: Player) -> None:
        """
        Konfiguracja gry.
        
        Args:
            player1 (Player): Pierwszy gracz
            player2 (Player): Drugi gracz
        """
        Display.clear_screen()
        print(f"\n{Fore.CYAN}=== TRYB DLA DWÓCH GRACZY ==={Style.RESET_ALL}")
        print("\nGracze wykonują ruchy naprzemiennie na wspólnej planszy.")
        
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
        self.current_player = 0
        self.moves = [0, 0]  # Resetujemy liczniki ruchów
        
        print(f"\nGracz 1: {Fore.CYAN}{self.player1.nickname}{Style.RESET_ALL}")
        print(f"Gracz 2: {Fore.MAGENTA}{self.player2.nickname}{Style.RESET_ALL}")
        print("\nNaciśnij dowolny klawisz, aby rozpocząć...")
        InputHandler.wait_key()

    def display_game_state(self) -> None:
        """Wyświetla aktualny stan gry."""
        if not self.needs_redraw:
            return
            
        Display.clear_screen()
        print(f"\n{Fore.YELLOW}=== TRYB DLA DWÓCH GRACZY ==={Style.RESET_ALL}")
        
        current_player = self.player1 if self.current_player == 0 else self.player2
        print(f"\nRuch gracza: {Fore.CYAN if self.current_player == 0 else Fore.MAGENTA}{current_player.nickname}{Style.RESET_ALL}")
        Display.display_board(
            self.board.get_board(),
            self.board.get_score(),
            current_player.nickname,
            get_theme_colors(),
            None,
            True,
            None
        )
        
        print(f"\nRuchy gracza 1: {self.moves[0]}")
        print(f"Ruchy gracza 2: {self.moves[1]}")
        print("\nR = Restart, Q = Wyjście")
        
        self.needs_redraw = False

    def _switch_player(self) -> None:
        """Przełącz na następnego gracza."""
        self.current_player = 1 - self.current_player  # Zmiana między 0 a 1

    def _process_command(self, command: str) -> None:
        """Przetwarzanie komend w grze."""
        if command == 'quit':
            self.running = False
        elif command in ['up', 'down', 'left', 'right']:
            if self.board.move(command):
                self.moves[self.current_player] += 1
                self.needs_redraw = True
                
                if self.board.has_won():
                    Display.clear_screen()
                    current_player = self.player1 if self.current_player == 0 else self.player2
                    print(f"\n{Fore.GREEN}Gratulacje! {current_player.nickname} wygrywa!{Style.RESET_ALL}")
                    print(f"Końcowy wynik: {self.board.get_score()}")
                    print(f"\nStatystyki ruchów:")
                    print(f"Gracz 1 ({self.player1.nickname}): {self.moves[0]} ruchów")
                    print(f"Gracz 2 ({self.player2.nickname}): {self.moves[1]} ruchów")
                    current_player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
                elif self.board.is_game_over():
                    Display.clear_screen()
                    print(f"\n{Fore.RED}Koniec gry!{Style.RESET_ALL}")
                    print(f"Końcowy wynik: {self.board.get_score()}")
                    print(f"\nStatystyki ruchów:")
                    print(f"Gracz 1 ({self.player1.nickname}): {self.moves[0]} ruchów")
                    print(f"Gracz 2 ({self.player2.nickname}): {self.moves[1]} ruchów")
                    self.player1.save_score(self.board.get_score())
                    self.player2.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
                else:
                    self._switch_player()

    def run(self, player1: Player, player2: Player) -> None:
        """
        Główna pętla gry w trybie dla dwóch graczy.
        
        Args:
            player1 (Player): Pierwszy gracz
            player2 (Player): Drugi gracz
        """
        self.setup_game(player1, player2)
        Display.clear_screen()
        
        while self.running:
            if self.needs_redraw:
                self.display_game_state()
                self.needs_redraw = False
            
            command = InputHandler.get_input()
            if command:
                self._process_command(command) 