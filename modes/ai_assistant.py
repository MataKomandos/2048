from typing import List, Tuple, Dict
import random
import numpy as np
from copy import deepcopy

class AI2048:
    
    def __init__(self, difficulty: str = "normal"):
        
        self.difficulty = difficulty
        self.hints_left = self._get_initial_hints()
        self.four_probability = self._get_four_probability()
        
    def _get_initial_hints(self) -> int:
        
        hints = {
            "easy": 10,
            "normal": 5,
            "hard": 3
        }
        return hints.get(self.difficulty, 5)
    
    def _get_four_probability(self) -> float:
        
        probabilities = {
            "easy": 0.1,
            "normal": 0.2,
            "hard": 0.3
        }
        return probabilities.get(self.difficulty, 0.2)
    
    def get_next_number(self) -> int:
        
        return 4 if random.random() < self.four_probability else 2
    
    def suggest_move(self, board: List[List[int]]) -> str:
        
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
        
        test_board = deepcopy(board)
        score = 0
        
        merged, moved = self._simulate_move(test_board, move)
        if not moved:
            return -float('inf')
        
        score += merged * 10
        
        score += self._evaluate_monotonicity(test_board) * 5
        
        score += self._count_empty(test_board) * 2.5
        
        score += self._evaluate_corners(test_board) * 3
        
        return score
    
    def _simulate_move(self, board: List[List[int]], move: str) -> Tuple[int, bool]:

        merged = 0
        size = len(board)
        changed = False
        
        if move in ['up', 'down']:
            for j in range(size):
                column = [board[i][j] for i in range(size)]
                if move == 'up':
                    new_column, m = self._merge_line(column)
                else:
                    new_column, m = self._merge_line(column[::-1])
                    new_column = new_column[::-1]
                merged += m
                if column != new_column:
                    changed = True
                for i in range(size):
                    board[i][j] = new_column[i]
        else:
            for i in range(size):
                row = board[i][:]
                if move == 'left':
                    new_row, m = self._merge_line(row)
                else:
                    new_row, m = self._merge_line(row[::-1])
                    new_row = new_row[::-1]
                merged += m
                if row != new_row:
                    changed = True
                board[i] = new_row
        
        return merged, changed
    
    def _merge_line(self, line: List[int]) -> Tuple[List[int], int]:
        
        size = len(line)
        line = [x for x in line if x != 0]
        merged = 0
        i = 0
        
        while i < len(line) - 1:
            if line[i] == line[i + 1]:
                line[i] *= 2
                line.pop(i + 1)
                merged += 1
            i += 1
        
        line.extend([0] * (size - len(line)))
        return line, merged
    
    def _evaluate_monotonicity(self, board: List[List[int]]) -> float:
        
        score = 0
        size = len(board)
        
        for i in range(size):
            for j in range(size - 1):
                if board[i][j] <= board[i][j + 1]:
                    score += 1
        
        for j in range(size):
            for i in range(size - 1):
                if board[i][j] <= board[i + 1][j]:
                    score += 1
        
        return score
    
    def _count_empty(self, board: List[List[int]]) -> int:
        
        return sum(row.count(0) for row in board)
    
    def _evaluate_corners(self, board: List[List[int]]) -> float:
        
        size = len(board)
        corners = [
            board[0][0],
            board[0][size-1],
            board[size-1][0],
            board[size-1][size-1]
        ]
        return sum(corners) / 4
    
    def check_game_over(self, board: List[List[int]], target: int) -> Tuple[bool, str]:

        if any(target in row for row in board):
            return True, "victory"
        
        if any(0 in row for row in board):
            return False, "ongoing"
        
        for move in ['up', 'down', 'left', 'right']:
            test_board = deepcopy(board)
            _, moved = self._simulate_move(test_board, move)
            if moved:
                return False, "ongoing"
        
        max_value = max(max(row) for row in board)
        if max_value * (2 ** (self._count_empty(board))) < target:
            return True, "impossible"
        
        return True, "game_over"
    
    def adjust_difficulty(self, score: int, moves: int, target_reached: bool) -> None:
        
        if target_reached and moves < 100:
            self.difficulty = "hard"
            self.four_probability = self._get_four_probability()
        elif score > 10000 and not target_reached:
            self.difficulty = "normal"
            self.four_probability = self._get_four_probability()
        elif score < 5000 and moves > 150:
            self.difficulty = "easy"
            self.four_probability = self._get_four_probability()
            self.hints_left = max(self.hints_left, 3)