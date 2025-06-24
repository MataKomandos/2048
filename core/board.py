import random
from typing import List, Tuple, Optional, Dict, Any
from collections import deque
from core.settings import Settings
import math
import json
import os
from datetime import datetime
from .error_handler import ErrorHandler, ValidationError, SaveError

class Board:
    """
    Klasa reprezentująca planszę gry 2048.
    
    Odpowiada za:
    - Przechowywanie i zarządzanie stanem planszy
    - Wykonywanie ruchów i łączenie kafelków
    - Obliczanie wyniku
    - Sprawdzanie warunków wygranej/przegranej
    - Zapisywanie i wczytywanie stanu planszy
    - Obsługę cofania ruchów
    """
    
    def __init__(self, size: int = 4):
        """
        Inicjalizacja planszy.
        
        Args:
            size (int): Rozmiar planszy (domyślnie: 4x4)
        """
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.last_move = None  # Information about the last move for animations
        self.move_history = deque(maxlen=5)  # Store last 5 moves
        self.undo_count = 0  # Number of undos used
        self.max_undos = 5  # Maximum number of undos per game
        self.settings = Settings()  # Dodanie instancji ustawień
        self.error_handler = ErrorHandler()
        self.history = []  # Historia ruchów do cofania
        self.max_history = 10  # Maksymalna liczba zapamiętanych ruchów
        self._add_new_tile()
        self._add_new_tile()
    
    def get_board(self) -> List[List[int]]:
        """
        Pobiera aktualny stan planszy.
        
        Returns:
            List[List[int]]: Dwuwymiarowa lista reprezentująca stan planszy
        """
        return self.board
    
    def get_score(self) -> int:
        """
        Pobiera aktualny wynik.
        
        Returns:
            int: Aktualny wynik gracza
        """
        return self.score
    
    def can_undo(self) -> bool:
        """
        Sprawdza czy możliwe jest cofnięcie ruchu.
        
        Returns:
            bool: True jeśli są dostępne cofnięcia ruchów
        """
        return len(self.history) > 0 and self.undo_count < self.max_undos
    
    def get_remaining_undos(self) -> int:
        """
        Pobiera liczbę pozostałych możliwych cofnięć.
        
        Returns:
            int: Liczba pozostałych cofnięć ruchów
        """
        return max(0, self.max_undos - self.undo_count)
    
    def undo_move(self) -> bool:
        """Undo the last move.
        
        Returns:
            bool: True if undo was successful
        """
        if not self.can_undo():
            return False
        
        previous_state = self.history.pop()
        self.board = previous_state["board"]
        self.score = previous_state["score"]
        self.undo_count += 1
        return True
    
    def calculate_difficulty(self) -> float:
        """Calculate current game state difficulty.
        
        Returns:
            float: Difficulty score (0-10)
        """
        # Czynniki wpływające na trudność:
# 1. Zapełnienie planszy (ile pól jest zajętych)
# 2. Różnorodność kafelek
# 3. Kafelki możliwe do połączenia (czy są takie same obok siebie)
# 4. Najwyższa wartość kafelka na planszy(jak blisko celu)

        
        # Calculate board fullness (0-1)
        non_zero_tiles = sum(1 for row in self.board for cell in row if cell != 0)
        fullness = non_zero_tiles / (self.size * self.size)
        
        # Calculate value disparity (0-1)
        values = [cell for row in self.board for cell in row if cell != 0]
        if values:
            max_val = max(values)
            avg_val = sum(values) / len(values)
            disparity = avg_val / max_val
        else:
            disparity = 0
        
        # Calculate mergeable tiles ratio (0-1)
        mergeable = self._count_mergeable_tiles()
        max_mergeable = 2 * self.size * (self.size - 1)
        mergeable_ratio = 1 - (mergeable / max_mergeable if max_mergeable > 0 else 0)
        
        # Calculate progress towards target (0-1)
        max_tile = max(max(row) for row in self.board)
        target = self.settings.get_target_value()
        progress = math.log2(max_tile) / math.log2(target) if max_tile > 0 else 0
                        #ile osiągnął             #ile poziomów brakuje
        # Combine factors with weights
        difficulty = (
            fullness * 3 +
            disparity * 2 +
            mergeable_ratio * 3 +
            progress * 2
        ) / 10
        
        return round(difficulty * 10, 1)
    
    def _count_mergeable_tiles(self) -> int:
        """Count number of mergeable tile pairs."""
        count = 0
        # Check horizontal merges
        # Sprawdzamy sąsiadujące poziomo kafelki w każdym wierszu – 
        # tylko niezerowe i równe mogą zostać połączone
        for i in range(self.size):
            for j in range(self.size - 1):  #dla kazdej kolumny, oprócz ostatniej
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i][j + 1]:
                    count += 1
        
        # Check vertical merges
        for i in range(self.size - 1): #dla każdego wiersza oprócz ostatniego
            for j in range(self.size):
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i + 1][j]:
                    count += 1
        
        return count
    
    def _add_new_tile(self) -> None:
        """Add a new tile on a random empty position."""
        empty_cells = [(i, j) for i in range(self.size) 
                      for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
            # Save information about the new tile for animations
            if self.last_move is None: #ostatni ruch
                self.last_move = {} #tworzy
            self.last_move['new_tile'] = (i, j) #zapisuje pozycje
    
    def move(self, direction: str) -> bool:
        """
        Wykonuje ruch w zadanym kierunku.
        
        Args:
            direction (str): Kierunek ruchu ('up', 'down', 'left', 'right')
            
        Returns:
            bool: True jeśli ruch został wykonany i zmienił stan planszy
        """
        if direction not in ['up', 'down', 'left', 'right']:
            raise ValidationError(f"Nieprawidłowy kierunek ruchu: {direction}")
        
        # Reset information about the last move
        self.last_move = {'merged': []}# o połączonych kaflekach
        
        # Save current state for undo
        current_state = {
            "board": [row[:] for row in self.board],
            "score": self.score
        }
        
        # Zapisujemy początkowy stan gry (kopiujemy planszę i wynik)
        initial_state = [row[:] for row in self.board]
        initial_score = self.score
        
        # Rotate board to handle all moves as left moves
        if direction == 'up':
            self._rotate_counterclockwise()
        elif direction == 'down':
            self._rotate_clockwise()
        elif direction == 'right':
            self._rotate_clockwise()
            self._rotate_clockwise()
        
        # Move tiles left
        for i in range(self.size):
            # Remove zeros
            row = [x for x in self.board[i] if x != 0]
            # Merge tiles
            j = 0
            while j < len(row) - 1:
                if row[j] == row[j + 1]:
                    row[j] *= 2
                    self.score += row[j]
                    row.pop(j + 1) #usuwa
                j += 1
            # Fill with zeros
            row.extend([0] * (self.size - len(row)))
            self.board[i] = row
        
        # Rotate back
        if direction == 'up':
            self._rotate_clockwise()
        elif direction == 'down':
            self._rotate_counterclockwise()
        elif direction == 'right':
            self._rotate_clockwise()
            self._rotate_clockwise()
        
        # Check if board changed
        changed = (initial_state != self.board) or (initial_score != self.score)
        if changed:
            self.history.append(current_state)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self._add_new_tile()
        
        return changed
    
    def _rotate_clockwise(self) -> None:
        """Rotate the board 90 degrees clockwise."""
        # Tworzymy nową planszę: nowy wiersz powstaje z kolumny starej planszy
    # i = indeks kolumny w starej planszy → będzie nowym wierszem
    # j = indeks wiersza w starej planszy, odczytywany od dołu do góry
        self.board = [[self.board[self.size - 1 - j][i] for j in range(self.size)] for i in range(self.size)]
                                        #nr wiersza #kolumny
    def _rotate_counterclockwise(self) -> None:
        """Rotate the board 90 degrees counterclockwise."""
        self.board = [[self.board[j][self.size - 1 - i] for j in range(self.size)] for i in range(self.size)]
    
    def has_won(self) -> bool:
        """
        Sprawdza czy gra została wygrana.
        
        Returns:
            bool: True jeśli osiągnięto wartość docelową z ustawień
        """
        target = self.settings.get_target_value()
        return any(target in row for row in self.board)
    
    def is_game_over(self) -> bool:
        """
        Sprawdza czy gra się zakończyła (brak możliwych ruchów).
        
        Returns:
            bool: True jeśli nie ma możliwych ruchów
        """
        # Check for empty cells
        if any(0 in row for row in self.board):
            return False
        
        return self._count_mergeable_tiles() == 0 #sprawdza możliwość połączenia
    
    def save_game(self, filepath: str) -> bool:
        """
        Zapisuje stan gry do pliku z zabezpieczeniami.
        
        Args:
            filepath (str): Ścieżka do pliku zapisu
            
        Returns:
            bool: True jeśli zapis się powiódł
        """
        try:
            game_data = {
                'board': self.board,
                'score': self.score,
                'size': self.size,
                'history': self.history,
                'timestamp': datetime.now().isoformat()
            }
            
            # Walidacja danych przed zapisem
            self.error_handler.validate_board(self.board)
            self.error_handler.validate_score(self.score)
            
            # Oblicz sumę kontrolną #zabeczpieczenie
            checksum = self.error_handler.calculate_checksum(game_data)
            
            save_data = {
                'game_data': game_data,
                'checksum': checksum
            }
            
            # Utwórz kopię zapasową przed zapisem
            self.error_handler.create_backup(save_data, filepath)
            
            # Zapisz główny plik
            with open(filepath, 'w') as f:
                json.dump(save_data, f)
            
            return True
            
        except Exception as e: #obsługa błędu
            self.error_handler.log_error(e, "Błąd podczas zapisywania gry")
            return False
    
    def load_game(self, filepath: str) -> bool:
        """
        Wczytuje stan gry z pliku z weryfikacją.
        
        Args:
            filepath (str): Ścieżka do pliku zapisu
            
        Returns:
            bool: True jeśli wczytanie się powiodło
        """
        try:
            # Sprawdź integralność pliku
            if not self.error_handler.verify_save_file(filepath):
                # Próba przywrócenia z kopii zapasowej
                backup_data = self.error_handler.restore_from_backup(filepath)
                if backup_data is None:
                    raise SaveError("Nie można wczytać gry - plik jest uszkodzony")
                game_data = backup_data['game_data']
            else:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                game_data = data['game_data'] 
            
            # Walidacja wczytanych danych #zabeczpieczenie przed manipulacją
            self.error_handler.validate_board(game_data['board'])
            self.error_handler.validate_score(game_data['score'])
            
            # Aktualizacja stanu gry
            self.board = game_data['board']
            self.score = game_data['score']
            self.size = game_data['size']
            self.history = game_data.get('history', [])
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas wczytywania gry")
            return False
    
    def undo(self) -> bool:
        """
        Cofa ostatni ruch.
        
        Returns:
            bool: Czy cofnięcie było możliwe
        """
        if not self.history:
            return False
        
        try:
            prev_state = self.history.pop() #pobiera ostatni stan gry
            self.board = prev_state['board']
            self.score = prev_state['score']
            return True
            
        except Exception as e: #błąd
            self.error_handler.log_error(e, "Błąd podczas cofania ruchu")
            return False
    
    def get_max_tile(self) -> int:
        """Get the value of the highest tile on the board.
        
        Returns:
            int: Value of the highest tile
        """
        return max(max(row) for row in self.board) 