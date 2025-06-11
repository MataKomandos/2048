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
    def __init__(self, size: int = 4):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.last_move = None
        self.move_history = deque(maxlen=5)
        self.undo_count = 0
        self.max_undos = 5
        self.settings = Settings()
        self.error_handler = ErrorHandler()
        self.history = []
        self.max_history = 10
        self._add_new_tile()
        self._add_new_tile()
    
    def get_board(self) -> List[List[int]]:
        return self.board
    
    def get_score(self) -> int:
        return self.score
    
    def can_undo(self) -> bool:
        return len(self.history) > 0 and self.undo_count < self.max_undos
    
    def get_remaining_undos(self) -> int:
        return max(0, self.max_undos - self.undo_count)
    
    def undo_move(self) -> bool:
        if not self.can_undo():
            return False
        
        previous_state = self.history.pop()
        self.board = previous_state["board"]
        self.score = previous_state["score"]
        self.undo_count += 1
        return True
    
    def calculate_difficulty(self) -> float:
        
        
        non_zero_tiles = sum(1 for row in self.board for cell in row if cell != 0)
        fullness = non_zero_tiles / (self.size * self.size)
        
        values = [cell for row in self.board for cell in row if cell != 0]
        if values:
            max_val = max(values)
            avg_val = sum(values) / len(values)
            disparity = avg_val / max_val
        else:
            disparity = 0
        
        mergeable = self._count_mergeable_tiles()
        max_mergeable = 2 * self.size * (self.size - 1)
        mergeable_ratio = 1 - (mergeable / max_mergeable if max_mergeable > 0 else 0)
        
        max_tile = max(max(row) for row in self.board)
        target = self.settings.get_target_value()
        progress = math.log2(max_tile) / math.log2(target) if max_tile > 0 else 0

        difficulty = (
            fullness * 3 +
            disparity * 2 +
            mergeable_ratio * 3 +
            progress * 2
        ) / 10
        
        return round(difficulty * 10, 1)
    
    def _count_mergeable_tiles(self) -> int:
        count = 0
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i][j + 1]:
                    count += 1
        
        for i in range(self.size - 1):
            for j in range(self.size):
                if self.board[i][j] != 0 and self.board[i][j] == self.board[i + 1][j]:
                    count += 1
        
        return count
    
    def _add_new_tile(self) -> None:
        empty_cells = [(i, j) for i in range(self.size) 
                      for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4
            if self.last_move is None:
                self.last_move = {}
            self.last_move['new_tile'] = (i, j)
    
    def move(self, direction: str) -> bool:
        if direction not in ['up', 'down', 'left', 'right']:
            raise ValidationError(f"Nieprawidłowy kierunek ruchu: {direction}")
        
        self.last_move = {'merged': []}
        
        current_state = {
            "board": [row[:] for row in self.board],
            "score": self.score
        }
        
        initial_state = [row[:] for row in self.board]
        initial_score = self.score
        
        if direction == 'up':
            self._rotate_counterclockwise()
        elif direction == 'down':
            self._rotate_clockwise()
        elif direction == 'right':
            self._rotate_clockwise()
            self._rotate_clockwise()
        
        for i in range(self.size):
            row = [x for x in self.board[i] if x != 0]
            j = 0
            while j < len(row) - 1:
                if row[j] == row[j + 1]:
                    row[j] *= 2
                    self.score += row[j]
                    row.pop(j + 1)
                j += 1
            row.extend([0] * (self.size - len(row)))
            self.board[i] = row

        if direction == 'up':
            self._rotate_clockwise()
        elif direction == 'down':
            self._rotate_counterclockwise()
        elif direction == 'right':
            self._rotate_clockwise()
            self._rotate_clockwise()
        
        changed = (initial_state != self.board) or (initial_score != self.score)
        if changed:
            self.history.append(current_state)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            self._add_new_tile()
        
        return changed
    
    def _rotate_clockwise(self) -> None:
        self.board = [[self.board[self.size - 1 - j][i] for j in range(self.size)] for i in range(self.size)]
    
    def _rotate_counterclockwise(self) -> None:
        self.board = [[self.board[j][self.size - 1 - i] for j in range(self.size)] for i in range(self.size)]
    
    def has_won(self) -> bool:
        target = self.settings.get_target_value()
        return any(target in row for row in self.board)
    
    def is_game_over(self) -> bool:
        if any(0 in row for row in self.board):
            return False
        
        return self._count_mergeable_tiles() == 0
    
    def save_game(self, filepath: str) -> bool:
        try:
            game_data = {
                'board': self.board,
                'score': self.score,
                'size': self.size,
                'history': self.history,
                'timestamp': datetime.now().isoformat()
            }
            
            self.error_handler.validate_board(self.board)
            self.error_handler.validate_score(self.score)
            
            checksum = self.error_handler.calculate_checksum(game_data)
            
            save_data = {
                'game_data': game_data,
                'checksum': checksum
            }
            
            self.error_handler.create_backup(save_data, filepath)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f)
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas zapisywania gry")
            return False
    
    def load_game(self, filepath: str) -> bool:
        try:
            if not self.error_handler.verify_save_file(filepath):
                backup_data = self.error_handler.restore_from_backup(filepath)
                if backup_data is None:
                    raise SaveError("Nie można wczytać gry - plik jest uszkodzony")
                game_data = backup_data['game_data']
            else:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                game_data = data['game_data']
            
            self.error_handler.validate_board(game_data['board'])
            self.error_handler.validate_score(game_data['score'])
            
            self.board = game_data['board']
            self.score = game_data['score']
            self.size = game_data['size']
            self.history = game_data.get('history', [])
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas wczytywania gry")
            return False
    
    def undo(self) -> bool:
        if not self.history:
            return False
        
        try:
            prev_state = self.history.pop()
            self.board = prev_state['board']
            self.score = prev_state['score']
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas cofania ruchu")
            return False
    
    def get_max_tile(self) -> int:
        return max(max(row) for row in self.board) 