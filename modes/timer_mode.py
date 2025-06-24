from typing import List, Optional
from core.board import Board
from core.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
from colorama import Fore, Back, Style
import random
import time
import threading
from .theme_colors import get_theme_colors

class TimerMode:
    """Tryb gry z limitem czasu na każdy ruch."""
    
    def __init__(self, size: int = 4):
        """
        Inicjalizacja trybu z czasem.
        
        Args:
            size (int): Rozmiar planszy
        """
        self.board = Board(size)
        self.running = True
        self.won = False
        self.moves = 0
        self.last_move_time = None
        self.move_time_limit = None  # Limit czasu na ruch w sekundach
        self.needs_redraw = True
        self.player = None
        self.timer_thread = None
    
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
        print(f"\nWybrano limit czasu na ruch: {self.move_time_limit} sekund")
        print("\nNaciśnij dowolny klawisz, aby rozpocząć...")
        InputHandler.wait_key()
        self._start_timer()
    
    def _countdown(self):
        """Odliczanie czasu."""
        last_display_time = 0
        display_interval = 1.0  # Odświeżaj ekran co 1 sekundę
        
        while self.running:
            current_time = time.time()
            
            # Odświeżaj ekran tylko co sekundę
            if current_time - last_display_time >= display_interval:
                self.needs_redraw = True
                last_display_time = current_time
            
            if self.running and self.last_move_time is not None:
                elapsed_time = current_time - self.last_move_time
                if elapsed_time > self.move_time_limit:
                    self.running = False
            
            time.sleep(0.01)  # Małe opóźnienie dla oszczędzania CPU
    
    def _start_timer(self):
        """Rozpocznij odliczanie."""
        self.last_move_time = time.time()
        self.running = True
        self.timer_thread = threading.Thread(target=self._countdown)
        self.timer_thread.daemon = True  # Wątek zostanie zakończony wraz z głównym wątkiem
        self.timer_thread.start()
    
    def _stop_timer(self):
        """Zatrzymaj odliczanie."""
        self.running = False
        if self.timer_thread:
            self.timer_thread.join()
    
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
    
    def _move(self, direction: str) -> bool:
        """
        Wykonaj ruch w zadanym kierunku.
        
        Args:
            direction (str): Kierunek ruchu ('up', 'down', 'left', 'right')
        
        Returns:
            bool: Czy ruch był możliwy
        """
        return self.board.move(direction)
    
    def _process_command(self, command: str) -> None:
        """Przetwarzanie komend w grze."""
        if command == 'quit':
            self._stop_timer()
            self.running = False
        elif command in ['up', 'down', 'left', 'right']:
            if self._move(command):
                self.last_move_time = time.time()  # Resetuj czas po udanym ruchu
                self.moves += 1
                self.needs_redraw = True
                
                if self.board.has_won():
                    self._stop_timer()
                    Display.display_win(self.board.get_score())
                    self.player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
                elif self.board.is_game_over():
                    self._stop_timer()
                    Display.display_game_over(self.board.get_score())
                    self.player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
    
    def run(self, player: Player) -> None:
        """Główna pętla gry w trybie czasowym."""
        self.setup_game(player)
        Display.clear_screen()
        
        while self.running:
            if self.needs_redraw:
                self.display_game_state()
                self.needs_redraw = False
            
            command = InputHandler.get_input()
            if command:
                self._process_command(command) 