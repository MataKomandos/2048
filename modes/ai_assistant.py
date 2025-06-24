from typing import List, Tuple, Dict
import random
import numpy as np
from copy import deepcopy

class AI2048:
    """Asystent AI dla gry 2048."""
    
    def __init__(self, difficulty: str = "normal"):
        """
        Inicjalizacja asystenta AI.
        
        Args:
            difficulty (str): Poziom trudności ('easy', 'normal', 'hard')
        """
        self.difficulty = difficulty
        self.hints_left = self._get_initial_hints()
        self.four_probability = self._get_four_probability()
        
    def _get_initial_hints(self) -> int:
        """Zwraca początkową liczbę podpowiedzi w zależności od poziomu trudności."""
        hints = {
            "easy": 10,
            "normal": 5,
            "hard": 3
        }
        return hints.get(self.difficulty, 5)
    
    def _get_four_probability(self) -> float:
        """Zwraca prawdopodobieństwo pojawienia się '4' w zależności od poziomu trudności."""
        probabilities = {
            "easy": 0.1,    # 10% szans na 4
            "normal": 0.2,  # 20% szans na 4
            "hard": 0.3     # 30% szans na 4
        }
        return probabilities.get(self.difficulty, 0.2)
    
    def get_next_number(self) -> int:
        """Zwraca następną wartość (2 lub 4) na podstawie poziomu trudności."""
        return 4 if random.random() < self.four_probability else 2
    
    def suggest_move(self, board: List[List[int]]) -> str:
        """
        Sugeruje najlepszy ruch na podstawie aktualnego stanu planszy.
        
        Args:
            board (List[List[int]]): Aktualny stan planszy
            
        Returns:
            str: Sugerowany kierunek ('up', 'down', 'left', 'right')
        """
        if self.hints_left <= 0:
            return None
        
        self.hints_left -= 1
        moves = ['up', 'down', 'left', 'right']
        best_score = -1
        best_move = None
        
        for move in moves:
            score = self._evaluate_move(board, move)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def _evaluate_move(self, board: List[List[int]], move: str) -> float:
        """
        Ocenia jakość ruchu na podstawie różnych kryteriów.
        
        Args:
            board (List[List[int]]): Stan planszy
            move (str): Kierunek ruchu
            
        Returns:
            float: Ocena ruchu
        """
        test_board = deepcopy(board)
        score = 0
        
        # Symuluj ruch
        merged, moved = self._simulate_move(test_board, move)
        if not moved:
            return -float('inf')
        
        # Kryteria oceny:
        # 1. Liczba połączonych bloków
        score += merged * 10
        
        # 2. Monotonność (preferuj układy rosnące/malejące)
        score += self._evaluate_monotonicity(test_board) * 5
        
        # 3. Puste pola
        score += self._count_empty(test_board) * 2.5
        
        # 4. Bloki o wysokich wartościach w rogach
        score += self._evaluate_corners(test_board) * 3
        
        return score
    
    def _simulate_move(self, board: List[List[int]], move: str) -> Tuple[int, bool]:
        """
        Symuluje ruch i zwraca liczbę połączeń oraz informację czy plansza się zmieniła.
        
        Returns:
            Tuple[int, bool]: (liczba_połączeń, czy_plansza_się_zmieniła)
        """
        merged = 0
        size = len(board)
        changed = False
        
        if move in ['up', 'down']:
            for j in range(size):
                # Wyciągnij kolumnę jako listę
                column = [board[i][j] for i in range(size)]
                if move == 'up':
                    # Dla ruchu w górę przetwarzamy kolumnę normalnie
                    new_column, m = self._merge_line(column)
                else:
                     # Dla ruchu w dół – odwracamy kolumnę, potem cofamy odwrócenie
                    new_column, m = self._merge_line(column[::-1]) #od lewej do prawej
                    new_column = new_column[::-1]
                    # Dodaj liczbę połączeń do łącznego wyniku
                merged += m
                if column != new_column:
                    changed = True
                     # Zapisz nową kolumnę z powrotem do planszy
                for i in range(size):
                    board[i][j] = new_column[i]
        else:  # left or right
            for i in range(size):
                row = board[i][:] #kopia
                if move == 'left':
                    new_row, m = self._merge_line(row)
                else:
                    new_row, m = self._merge_line(row[::-1])
                    #po połączeniu wracamy
                    new_row = new_row[::-1]
                merged += m
                if row != new_row:
                    changed = True
                board[i] = new_row
        
        return merged, changed
    
    def _merge_line(self, line: List[int]) -> Tuple[List[int], int]:
        """
        Łączy bloki w linii i zwraca nową linię oraz liczbę połączeń.
        
        Returns:
            Tuple[List[int], int]: (nowa_linia, liczba_połączeń)
        """
        size = len(line)
        # Usuń zera
        line = [x for x in line if x != 0]
        merged = 0
        i = 0
        
        # Łącz sąsiednie takie same wartości
        while i < len(line) - 1:
            if line[i] == line[i + 1]:
                line[i] *= 2
                line.pop(i + 1)
                merged += 1
            i += 1
        
        # Uzupełnij zerami do oryginalnej długości
        line.extend([0] * (size - len(line)))
        return line, merged
    
    def _evaluate_monotonicity(self, board: List[List[int]]) -> float:
        """Ocenia monotonność układu (preferuj układy rosnące/malejące)."""
        score = 0
        size = len(board)
        
        # Sprawdź wiersze
        for i in range(size):
            for j in range(size - 1):
                if board[i][j] <= board[i][j + 1]:
                    score += 1
        
        # Sprawdź kolumny
        for j in range(size):
            for i in range(size - 1):
                if board[i][j] <= board[i + 1][j]:
                    score += 1
        
        return score
    
    def _count_empty(self, board: List[List[int]]) -> int:
        """Liczy puste pola na planszy."""
        return sum(row.count(0) for row in board)
    
    def _evaluate_corners(self, board: List[List[int]]) -> float:
        """Ocenia wartości w rogach planszy."""
        size = len(board)
        corners = [
            board[0][0],
            board[0][size-1],
            board[size-1][0],
            board[size-1][size-1]
        ]
        return sum(corners) / 4

    def check_game_over(self, board: List[List[int]], target: int) -> Tuple[bool, str]:
        """
        Sprawdza, czy gra jest skończona i czy jest możliwość wygranej.
        
        Args:
            board (List[List[int]]): Stan planszy
            target (int): Wartość docelowa
            
        Returns:
            Tuple[bool, str]: (czy_koniec, komunikat)
        """
        # Sprawdź czy osiągnięto cel
        if any(target in row for row in board):
            return True, "victory"
        
        # Sprawdź czy są puste pola
        if any(0 in row for row in board):
            return False, "ongoing"
        
        # Sprawdź możliwe ruchy
        for move in ['up', 'down', 'left', 'right']:
            test_board = deepcopy(board)
            _, moved = self._simulate_move(test_board, move)
            if moved:
                return False, "ongoing"
        
        # Sprawdź czy jest możliwość osiągnięcia celu
        max_value = max(max(row) for row in board)
        if max_value * (2 ** (self._count_empty(board))) < target:
            return True, "impossible"
        
        return True, "game_over"
    
    def adjust_difficulty(self, score: int, moves: int, target_reached: bool) -> None:
        """
        Dostosowuje trudność na podstawie wyników gracza.
        
        Args:
            score (int): Wynik gracza
            moves (int): Liczba wykonanych ruchów
            target_reached (bool): Czy osiągnięto wartość docelową
        """
        if target_reached and moves < 100:  # Gracz radzi sobie bardzo dobrze
            self.difficulty = "hard"
            self.four_probability = self._get_four_probability()
        elif score > 10000 and not target_reached:  # Gracz radzi sobie dobrze
            self.difficulty = "normal"
            self.four_probability = self._get_four_probability()
        elif score < 5000 and moves > 150:  # Gracz ma trudności
            self.difficulty = "easy"
            self.four_probability = self._get_four_probability()
            self.hints_left = max(self.hints_left, 3)  # Dodaj dodatkowe podpowiedzi 