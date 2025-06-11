from typing import List, Dict, Any, Optional
from core.board import Board
from core.player import Player
from ui.display import Display
from ui.input_handler import InputHandler
from colorama import Fore, Style
from .theme_colors import get_theme_colors
import time

class ChallengeMode:
    
    CHALLENGES = {
        "Symetria": {
            "board": [
                [2, 0, 0, 2],
                [0, 4, 4, 0],
                [0, 4, 4, 0],
                [2, 0, 0, 2]
            ],
            "goal": "Osiągnij 256 zachowując symetrię planszy",
            "target": 256
        },
        "Wieża": {
            "board": [
                [0, 0, 0, 2],
                [0, 0, 2, 4],
                [0, 2, 4, 8],
                [2, 4, 8, 16]
            ],
            "goal": "Stwórz wieżę z 2048 w rogu",
            "target": 2048
        },
        "Spirala": {
            "board": [
                [2, 2, 2, 2],
                [0, 0, 0, 2],
                [2, 0, 0, 2],
                [2, 2, 2, 2]
            ],
            "goal": "Utwórz spiralę z liczb",
            "target": 512
        }
    }
    
    def __init__(self, challenge_name: str):
        
        self.challenge = self.CHALLENGES[challenge_name]
        self.board = Board(4)
        self.board.board = [row[:] for row in self.challenge["board"]]
        self.running = True
        self.won = False
        self.moves = 0
        self.target_moves = 50
        self.needs_redraw = True
        self.challenge_name = challenge_name
    
    @classmethod
    def list_challenges(cls) -> List[str]:
        return list(cls.CHALLENGES.keys())
    
    def run(self, player: Player) -> None:
        self.player = player
        Display.clear_screen()
        
        while self.running:
            if self.needs_redraw:
                self.display_game_state()
                self.needs_redraw = False
            
            command = InputHandler.get_input()
            if command:
                self._process_command(command)
    
    def display_game_state(self) -> None:
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
        
        print(f"\n{Fore.YELLOW}=== TRYB WYZWANIA ==={Style.RESET_ALL}")
        print(f"Pozostałe ruchy: {self.target_moves - self.moves}")
        print(f"Wykonane ruchy: {self.moves}")
        print("\nR = Restart, Q = Wyjście")
        
        self.needs_redraw = False
    
    def _check_challenge_complete(self) -> bool:
        
        max_value = max(max(row) for row in self.board.board)
        return max_value >= self.challenge["target"]
    
    def _process_command(self, command: str) -> None:

        if command == 'quit':
            self.running = False
        elif command in ['up', 'down', 'left', 'right']:
            if self.board.move(command):
                self.moves += 1
                self.needs_redraw = True
                
                if self.moves >= self.target_moves:
                    Display.clear_screen()
                    print(f"\n{Fore.RED}Koniec gry! Wykorzystano wszystkie ruchy.{Style.RESET_ALL}")
                    print(f"Końcowy wynik: {self.board.get_score()}")
                    InputHandler.wait_key()
                    self.running = False
                    
                elif self._check_challenge_complete():
                    Display.clear_screen()
                    print(f"\n{Fore.GREEN}Gratulacje! Wyzwanie ukończone!{Style.RESET_ALL}")
                    print(f"Końcowy wynik: {self.board.get_score()}")
                    print(f"Wykorzystane ruchy: {self.moves}/{self.target_moves}")
                    self.player.save_score(self.board.get_score())
                    InputHandler.wait_key()
                    self.running = False
                elif self.board.is_game_over():
                    Display.display_game_over(self.board.get_score())
                    print(f"Wykorzystane ruchy: {self.moves}/{self.target_moves}")
                    InputHandler.wait_key()
                    self.running = False 