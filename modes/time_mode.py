import time
from typing import Optional
from core.board import Board
from core.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
from colorama import Fore, Style
from core.error_handler import ErrorHandler
from core.database_manager import DatabaseManager
from .theme_colors import get_theme_colors

class TimeMode:
    """Tryb gry z limitem czasu na ruch."""
    
    def __init__(self):
        """Inicjalizacja trybu czasowego."""
        self.board = None
        self.player = None
        self.moves = 0
        self.needs_redraw = True
        self.running = True
        self.last_move_time = None
        self.move_time_limit = None  # Limit czasu na ruch w sekundach
        self.error_handler = ErrorHandler()
        self.db_manager = DatabaseManager()
        self.db_player = None
        self.db_game = None
    
    def setup_game(self, player: Player) -> None:
        """
        Konfiguracja gry.
        
        Args:
            player (Player): Obiekt gracza
        """
        Display.clear_screen()
        print(f"\n{Fore.CYAN}=== TRYB NA CZAS ==={Style.RESET_ALL}")
        print("\nWybierz limit czasu na ruch:")
        print("1. 5 sekund")
        print("2. 10 sekund")
        print("3. 15 sekund")
        
        while True:
            choice = InputHandler.get_menu_input()
            if choice in [1, 2, 3]:
                self.move_time_limit = {1: 5, 2: 10, 3: 15}[choice]  # w sekundach
                break
            print("\nNieprawidłowy wybór. Spróbuj ponownie.")
        
        self.player = player
        self.board = Board()
        self.last_move_time = time.time()  # Rozpocznij odliczanie od teraz
        
        print(f"\nWybrano limit czasu na ruch: {self.move_time_limit} sekund")
        print("\nNaciśnij dowolny klawisz, aby rozpocząć...")
        InputHandler.wait_key()
    
    def display_game_state(self) -> None:
        """Wyświetla aktualny stan gry."""
        if not self.needs_redraw:
            return
            
        Display.clear_screen()
        Display.display_board(
            self.board.get_board(),
            self.board.get_score(),
            self.player.nickname,
            get_theme_colors(),
            None,
            True,
            None
        )
        
        if self.last_move_time is not None:
            elapsed_time = int(time.time() - self.last_move_time)
            remaining_time = max(0, self.move_time_limit - elapsed_time)
            
            print(f"\n{Fore.YELLOW}=== TRYB NA CZAS ==={Style.RESET_ALL}")
            print(f"Pozostały czas na ruch: {remaining_time} sekund")
            print(f"Wykonane ruchy: {self.moves}")
            print("\nR = Restart, Q = Wyjście")
        
        self.needs_redraw = False
    
    def run(self, player: Player) -> None:
        """Główna pętla gry w trybie czasowym."""
        self.setup_game(player)
        Display.clear_screen()
        last_display_time = 0
        display_interval = 1.0  # Odświeżaj ekran co 1 sekundę
        
        while self.running:
            current_time = time.time()
            
            # Odświeżaj ekran tylko co sekundę lub po ruchu
            if current_time - last_display_time >= display_interval:
                self.needs_redraw = True
                last_display_time = current_time
            
            if self.needs_redraw:
                self.display_game_state()
                self.needs_redraw = False
            
            # Sprawdź czy nie przekroczono limitu czasu na ruch
            if current_time - self.last_move_time > self.move_time_limit:
                self._handle_timeout()
                break
            
            command = InputHandler.get_input()
            if command:
                self._process_command(command)
            
            # Małe opóźnienie dla oszczędzania CPU
            time.sleep(0.01)
    
    def _handle_timeout(self) -> None:
        """Obsługa przekroczenia czasu na ruch."""
        Display.clear_screen()
        print(f"\n{Fore.RED}Koniec czasu na ruch!{Style.RESET_ALL}")
        print(f"Końcowy wynik: {self.board.get_score()}")
        self.player.save_score(self.board.get_score())
        InputHandler.wait_key()
        self.running = False
    
    def _process_command(self, command: str) -> None:
        """Przetwarzanie komend w grze."""
        if command == 'quit':
            self.running = False
        elif command in ['up', 'down', 'left', 'right']:
            if self.board.move(command):
                self.last_move_time = time.time()  # Resetuj czas po udanym ruchu
                self.moves += 1
                self.needs_redraw = True
                
                if self.board.has_won():
                    Display.display_win(self.board.get_score())
                    self.player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
                elif self.board.is_game_over():
                    Display.display_game_over(self.board.get_score())
                    self.player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False 