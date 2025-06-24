from typing import List, Optional
from core.board import Board
from core.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
from colorama import Fore, Back, Style
import random
import time
from .theme_colors import get_theme_colors
from core.error_handler import ErrorHandler
from core.database_manager import DatabaseManager

class ObstaclesMode:
    """Tryb gry z przeszkodami."""
    
    def __init__(self):
        """Inicjalizacja trybu z przeszkodami."""
        self.board = None
        self.player = None
        self.obstacles = set()  # Zbiór współrzędnych przeszkód (x, y)
        self.num_obstacles = 0  # Liczba przeszkód
        self.moves = 0
        self.needs_redraw = True
        self.running = True
        self.error_handler = ErrorHandler()
        self.db_manager = DatabaseManager()
        self.db_player = None
        self.db_game = None
    
    def _place_obstacles(self, num_obstacles: int) -> None:
        """
        Umieść przeszkody na planszy.
        
        Args:
            num_obstacles (int): Liczba przeszkód do umieszczenia
        """
        self.num_obstacles = num_obstacles
        empty_cells = []
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            positions = random.sample(empty_cells, min(num_obstacles, len(empty_cells)))
            self.obstacles = set(positions)
    
    def setup_game(self, player: Player) -> None:
        """
        Konfiguracja gry.
        
        Args:
            player (Player): Obiekt gracza
        """
        Display.clear_screen()
        print(f"\n{Fore.CYAN}=== TRYB Z PRZESZKODAMI ==={Style.RESET_ALL}")
        print("\nWybierz poziom trudności:")
        print("1. Łatwy (2 przeszkody)")
        print("2. Normalny (4 przeszkody)")
        print("3. Trudny (6 przeszkód)")
        
        while True:
            choice = InputHandler.get_menu_input()
            if choice in [1, 2, 3]:
                num_obstacles = {1: 2, 2: 4, 3: 6}[choice]
                break
            print("\nNieprawidłowy wybór. Spróbuj ponownie.")
        
        self.player = player
        self.board = Board()
        self._place_obstacles(num_obstacles)
        
        print(f"\nUstawiono {num_obstacles} przeszkód na planszy.")
        print("\nNaciśnij dowolny klawisz, aby rozpocząć...")
        InputHandler.wait_key()
    
    def display_game_state(self) -> None:
        """Wyświetla aktualny stan gry."""
        if not self.needs_redraw:
            return
            
        Display.clear_screen()
        
        # Przygotuj planszę z przeszkodami
        board = self.board.get_board()
        display_board = []
        for i in range(self.board.size):
            row = []
            for j in range(self.board.size):
                if (i, j) in self.obstacles:
                    row.append('X')  # Oznacz przeszkody jako 'X'
                else:
                    row.append(board[i][j])
            display_board.append(row)
        
        # Wyświetl planszę z przeszkodami
        Display.display_board(
            display_board,
            self.board.get_score(),
            self.player.nickname,
            get_theme_colors(),  # Używamy kolorów z motywu
            None,
            True,
            None
        )
        
        print(f"\n{Fore.YELLOW}=== TRYB Z PRZESZKODAMI ==={Style.RESET_ALL}")
        print(f"Wykonane ruchy: {self.moves}")
        print(f"\nPola oznaczone {Fore.WHITE}{Back.RED} X {Style.RESET_ALL} są zablokowane!")
        print("\nR = Restart, Q = Wyjście")
        
        self.needs_redraw = False
    
    def _get_empty_cells(self) -> List[tuple]:
        """Znajdź wszystkie puste komórki na planszy."""
        empty_cells = []
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.board[i][j] == 0 and (i, j) not in self.obstacles:
                    empty_cells.append((i, j))
        return empty_cells
    
    def _place_random_obstacles(self) -> None:
        """Umieść przeszkody na losowych pustych polach."""
        # Usuń stare przeszkody
        self.obstacles.clear()
        
        # Znajdź puste pola
        empty_cells = []
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.board[i][j] == 0:
                    empty_cells.append((i, j))
        
        # Wybierz losowe pozycje (tyle ile było na początku gry)
        if empty_cells:
            positions = random.sample(empty_cells, min(self.num_obstacles, len(empty_cells)))
            self.obstacles = set(positions)
    
    def _move_line(self, line: list, obstacles_pos: set) -> tuple[list, bool]:
        """
        Przesuń pojedynczą linię z uwzględnieniem przeszkód.
        
        Args:
            line (list): Lista liczb do przesunięcia
            obstacles_pos (set): Pozycje przeszkód w linii
        
        Returns:
            tuple[list, bool]: (Nowa linia, Czy nastąpiła zmiana)
        """
        size = len(line)
        new_line = [0] * size
        changed = False
        write_pos = 0
        
        # Przesuwamy liczby w lewo, zatrzymując się na przeszkodach
        for read_pos in range(size):
            if read_pos in obstacles_pos:
                write_pos = read_pos + 1  # Przeskocz na następną pozycję po przeszkodzie
                new_line[read_pos] = 0  # Przeszkoda blokuje to pole, puste ale niedostępne
                continue
                
            if line[read_pos] == 0:
                continue
                
            # Jeśli mamy przeszkodę przed write_pos, przesuń write_pos za nią
            while write_pos in obstacles_pos:
                write_pos += 1
                
            if write_pos >= size:
                break
                
            if new_line[write_pos] == 0:
                new_line[write_pos] = line[read_pos]
                changed = changed or write_pos != read_pos
            elif new_line[write_pos] == line[read_pos]:
                new_line[write_pos] *= 2
                self.board.score += new_line[write_pos]
                write_pos += 1
                changed = True
            else:
                write_pos += 1
                # Jeśli następna pozycja jest przeszkodą, przesuń za nią
                while write_pos in obstacles_pos:
                    write_pos += 1
                if write_pos < size:
                    new_line[write_pos] = line[read_pos]
                    changed = changed or write_pos != read_pos
        
        return new_line, changed

    def _move(self, direction: str) -> bool:
        """
        Wykonaj ruch w zadanym kierunku z uwzględnieniem przeszkód.
        
        Args:
            direction (str): Kierunek ruchu ('up', 'down', 'left', 'right')
        
        Returns:
            bool: Czy ruch był możliwy
        """
        size = self.board.size
        changed = False
        
        if direction in ['left', 'right']:
            for i in range(size):
                # Znajdź przeszkody w tym wierszu
                obstacles_in_row = {j for j in range(size) if (i, j) in self.obstacles}
                line = self.board.board[i]
                
                if direction == 'right':
                    line = line[::-1]
                    obstacles_in_row = {size - 1 - pos for pos in obstacles_in_row}
                
                new_line, line_changed = self._move_line(line, obstacles_in_row)
                
                if direction == 'right':
                    new_line = new_line[::-1]
                
                if line_changed:
                    changed = True
                    self.board.board[i] = new_line
        else:  # up or down
            for j in range(size):
                # Znajdź przeszkody w tej kolumnie
                obstacles_in_col = {i for i in range(size) if (i, j) in self.obstacles}
                line = [self.board.board[i][j] for i in range(size)]
                
                if direction == 'down':
                    line = line[::-1]
                    obstacles_in_col = {size - 1 - pos for pos in obstacles_in_col}
                
                new_line, line_changed = self._move_line(line, obstacles_in_col)
                
                if direction == 'down':
                    new_line = new_line[::-1]
                
                if line_changed:
                    changed = True
                    for i in range(size):
                        self.board.board[i][j] = new_line[i]
        
        # Jeśli ruch był możliwy, dodaj nową liczbę na pustym polu (omijając przeszkody)
        if changed:
            empty_cells = []
            for i in range(size):
                for j in range(size):
                    if self.board.board[i][j] == 0 and (i, j) not in self.obstacles:
                        empty_cells.append((i, j))
            
            if empty_cells:
                i, j = random.choice(empty_cells)
                self.board.board[i][j] = 2 if random.random() < 0.9 else 4
        
        return changed
    
    def _process_command(self, command: str) -> None:
        """Przetwarzanie komend w grze."""
        if command == 'quit':
            self.running = False
        elif command in ['up', 'down', 'left', 'right']:
            # Wykonaj ruch z uwzględnieniem przeszkód
            if self._move(command):
                # Po udanym ruchu, zmień pozycje przeszkód
                self._place_random_obstacles()
                self.needs_redraw = True
                self.moves += 1
                
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
    
    def run(self, player: Player) -> None:
        """Główna pętla gry w trybie z przeszkodami."""
        self.setup_game(player)  # Najpierw konfigurujemy grę
        Display.clear_screen()
        
        while self.running:
            if self.needs_redraw:
                self.display_game_state()
                self.needs_redraw = False  # Dodajemy to, żeby nie odświeżać ciągle
            
            command = InputHandler.get_input()
            if command:
                self._process_command(command) 