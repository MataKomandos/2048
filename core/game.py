import time
from typing import Optional, Dict, List, Any
import json
import os
import sys
from pathlib import Path
from colorama import Fore, Back, Style
import signal
from datetime import datetime, timedelta

from core.board import Board
from core.player import Player
from core.settings import Settings
from core.save_manager import SaveManager
from core.database import DatabaseManager
from ui.display import Display
from ui.input_handler import InputHandler
from core.statistics import Statistics
from core.error_handler import ErrorHandler, GameError

class Game:
    
    def __init__(self, size: int = None, player: Optional[Player] = None):
        
        self.settings = Settings()
        self.save_manager = SaveManager()
        self.db_manager = DatabaseManager()
        self.board = Board(size if size else self.settings.get_board_size())
        self.running = True
        self.won = False
        self.player = player
        self.needs_redraw = True
        self.statistics = Statistics()
        self.error_handler = ErrorHandler()
        self.last_autosave = datetime.now()
        self.autosave_interval = timedelta(minutes=5)
        self.db_game = None
        
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

        if self.player:
            self.db_player = self.db_manager.add_player(self.player.nickname)
            self.db_game = self.db_manager.start_game(self.db_player, "classic")
    
    def _handle_interrupt(self, signum, frame):
        
        print("\nPrzechwycono sygnał przerwania. Zapisywanie stanu gry...")
        self._emergency_save()
        sys.exit(0)
    
    def _emergency_save(self) -> None:
        
        if self.board and self.player:
            try:
                game_state = self.get_game_state()
                self.save_manager.create_autosave(game_state)
                print("Stan gry został zapisany.")
            except Exception as e:
                self.error_handler.log_error(e, "Błąd podczas awaryjnego zapisu")
    
    def get_game_state(self) -> Dict[str, Any]:
        
        return {
            "board": self.board.get_board(),
            "score": self.board.get_score(),
            "size": self.board.size,
            "won": self.won,
            "player_nickname": self.player.nickname if self.player else None,
            "settings": self.settings.settings,
            "timestamp": datetime.now().isoformat()
        }
    
    def load_game_state(self, state: Dict[str, Any]) -> None:
        
        self.board = Board(state["size"])
        self.board.board = state["board"]
        self.board.score = state["score"]
        self.won = state["won"]
        if state["player_nickname"]:
            self.player = Player(state["player_nickname"])
        if "settings" in state:
            self.settings.settings = state["settings"]
            self.settings.save_settings()
            self.running = True
        self.last_autosave = datetime.fromisoformat(state["timestamp"])
    
    def save_game(self, filename: str = "save_game.json") -> bool:
        
        try:
            game_state = self.get_game_state()
            return self.save_manager.save_game(game_state, filename)
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas zapisywania gry")
            return False
    
    def load_game(self, filename: str = "save_game.json") -> bool:
        
        try:
            state = self.save_manager.load_game(filename)
            if state:
                self.load_game_state(state)
                return True
            return False
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas wczytywania gry")
            return False
    
    def create_checkpoint(self, name: Optional[str] = None) -> str:
        
        return self.save_manager.create_checkpoint(self.get_game_state(), name)
    
    def load_checkpoint(self, filename: str) -> bool:
        
        game_data = self.save_manager.load_checkpoint(filename)
        if game_data:
            self.load_game_state(game_data)
            return True
        return False
    
    def export_game(self, filepath: str) -> bool:
        
        return self.save_manager.export_game(self.get_game_state(), filepath)
    
    def import_game(self, filepath: str) -> bool:
        
        state = self.save_manager.import_game(filepath)
        if state:
            self.load_game_state(state)
            return True
        return False
    
    @staticmethod
    def display_saves_menu() -> None:
        
        while True:
            Display.clear_screen()
            print("\n=== ZAPISY I CHECKPOINTY ===\n")
            print("1. Wczytaj zapis")
            print("2. Utwórz checkpoint")
            print("3. Wczytaj checkpoint")
            print("4. Eksportuj grę")
            print("5. Importuj grę")
            print("6. Powrót do menu głównego\n")
            
            choice = InputHandler.get_menu_input()
            
            if choice == 1:
                Game._display_load_game_menu()
            elif choice == 2:
                Game._create_checkpoint_menu()
            elif choice == 3:
                Game._load_checkpoint_menu()
            elif choice == 4:
                Game._export_game_menu()
            elif choice == 5:
                Game._import_game_menu()
            elif choice == 6:
                break

    @staticmethod
    def _display_load_game_menu() -> None:
        
        Display.clear_screen()
        print("\n=== WCZYTYWANIE ZAPISU ===\n")
        print("Dostępne zapisy:\n")
        
        save_manager = SaveManager()
        saves = save_manager.list_saves()
        
        if not saves:
            print("Brak dostępnych zapisów!")
            InputHandler.wait_key()
            return
            
        for i, save in enumerate(saves, 1):
            timestamp = datetime.fromisoformat(save['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. {save['name']} (Wynik: {save['score']}, Data: {timestamp})")
        
        print("\nWybierz numer zapisu lub 0 aby wrócić:")
        choice = InputHandler.get_number_input(0, len(saves))
        
        if choice == 0:
            return
            
        selected_save = saves[choice - 1]['name']
        if save_manager.load_game(selected_save):
            print("\nZapis został wczytany pomyślnie!")
        else:
            print("\nBłąd podczas wczytywania zapisu!")
        InputHandler.wait_key()

    @staticmethod
    def _create_checkpoint_menu() -> None:
        
        Display.clear_screen()
        print("\n=== TWORZENIE CHECKPOINTU ===\n")
        print("Podaj nazwę checkpointu (lub zostaw puste dla automatycznej nazwy):")
        name = InputHandler.get_text_input(allow_empty=True)
        
        save_manager = SaveManager()
        game = Game()
        
        checkpoint_name = save_manager.create_checkpoint(game.get_game_state(), name if name else None)
        
        if checkpoint_name:
            print(f"\nCheckpoint '{checkpoint_name}' został utworzony!")
        else:
            print("\nBłąd podczas tworzenia checkpointu!")
        InputHandler.wait_key()

    @staticmethod
    def _load_checkpoint_menu() -> None:

        Display.clear_screen()
        print("\n=== WCZYTYWANIE CHECKPOINTU ===\n")
        print("Dostępne checkpointy:\n")
        
        save_manager = SaveManager()
        checkpoints = save_manager.list_checkpoints()
        
        if not checkpoints:
            print("Brak dostępnych checkpointów!")
            InputHandler.wait_key()
            return
            
        for i, cp in enumerate(checkpoints, 1):
            timestamp = datetime.fromisoformat(cp['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. {cp['name']} (Wynik: {cp['score']}, Data: {timestamp})")
        
        print("\nWybierz numer checkpointu lub 0 aby wrócić:")
        choice = InputHandler.get_number_input(0, len(checkpoints))
        
        if choice == 0:
            return
            
        selected_checkpoint = checkpoints[choice - 1]['name']
        game = Game()
        
        if game.load_checkpoint(selected_checkpoint):
            print("\nCheckpoint został wczytany pomyślnie!")
        else:
            print("\nBłąd podczas wczytywania checkpointu!")
        InputHandler.wait_key()

    @staticmethod
    def _export_game_menu() -> None:
        
        Display.clear_screen()
        print("\n=== EKSPORT GRY ===\n")
        print("Podaj nazwę pliku eksportu (bez rozszerzenia):")
        filename = InputHandler.get_text_input()
        
        if not filename:
            return
            
        filepath = f"{filename}.2048"
        game = Game()
        
        if game.export_game(filepath):
            print(f"\nGra została wyeksportowana do pliku: {filepath}")
        else:
            print("\nBłąd podczas eksportu gry!")
        InputHandler.wait_key()

    @staticmethod
    def _import_game_menu() -> None:
        
        Display.clear_screen()
        print("\n=== IMPORT GRY ===\n")
        print("Podaj nazwę pliku do importu (bez rozszerzenia):")
        filename = InputHandler.get_text_input()
        
        if not filename:
            return
            
        filepath = f"{filename}.2048"
        game = Game()
        
        if game.import_game(filepath):
            print("\nGra została zaimportowana pomyślnie!")
        else:
            print("\nBłąd podczas importu gry!")
        InputHandler.wait_key()
    
    def run(self) -> None:
        
        try:
            Display.clear_screen()
            self.needs_redraw = True
            
            while self.running:
                if self.needs_redraw:
                    difficulty = self.board.calculate_difficulty()
                    Display.display_board(
                        self.board.get_board(),
                        self.board.get_score(),
                        self.player.nickname if self.player else None,
                        self.settings.get_theme_colors(),
                        difficulty,
                        self.board.can_undo(),
                        self.board.get_remaining_undos()
                    )
                    self.needs_redraw = False
                
                if self.board.is_game_over():
                    difficulty = self.board.calculate_difficulty()
                    Display.display_board(
                        self.board.get_board(),
                        self.board.get_score(),
                        self.player.nickname if self.player else None,
                        self.settings.get_theme_colors(),
                        difficulty,
                        self.board.can_undo(),
                        self.board.get_remaining_undos()
                    )
                    Display.display_game_over(self.board.get_score())
                    if self.db_game:
                        self.db_manager.complete_game(self.db_game)
                    self.statistics.end_session()
                    self.statistics.display_session_stats()
                    if self.player:
                        self.player.save_score(self.board.get_score())
                    self.running = False
                    InputHandler.wait_key()
                    break
                
                if not self.won and self.board.has_won():
                    self.won = True
                    Display.display_win(self.board.get_score())
                    InputHandler.wait_key()
                    self.needs_redraw = True
                
                command = InputHandler.get_input()
                if command:
                    self.process_command(command)
                
                time.sleep(0.01)
                
                self._check_autosave()
            
        except Exception as e:
            self.error_handler.log_error(e, "Krytyczny błąd w głównej pętli gry")
            self._emergency_save()
        finally:
            self._emergency_save()
    
    def process_command(self, command: str) -> None:

        if command == 'quit':
            if self.db_game:
                self.db_manager.complete_game(self.db_game)
            self.save_game()
            self.running = False
        elif command == 'restart':
            Display.clear_screen()
            print("\nEnter your nickname: ")
            nickname = InputHandler.get_text_input()
            self.player = Player(nickname)
            self.db_player = self.db_manager.add_player(nickname)
            self.db_game = self.db_manager.start_game(self.db_player, "classic")
            self.board = Board(self.board.size)
            self.won = False
            self.needs_redraw = True
        elif command == 'help':
            Display.display_controls()
            InputHandler.wait_key()
            self.needs_redraw = True
        elif command == 'undo':
            if self.board.undo_move():
                self.needs_redraw = True
        elif command in ['up', 'down', 'left', 'right']:
            old_score = self.board.get_score()
            if self.board.move(command):
                self.needs_redraw = True
                if self.db_game:
                    score_change = self.board.get_score() - old_score
                    self.db_manager.add_move(self.db_game, command, score_change)
                    self.db_manager.update_game(self.db_game, self.board.get_score(), self.board.get_max_tile())
                
                self.statistics.update_move_stats(command, self.board.get_board(), self.board.get_score())
                self._check_autosave()
                
                if self.board.has_won():
                    self.won = True
                    Display.display_win(self.board.get_score())
                    InputHandler.wait_key()
                    self.needs_redraw = True
                elif self.board.is_game_over():
                    Display.display_game_over(self.board.get_score())
                    InputHandler.wait_key()
                    self.needs_redraw = True
    
    @staticmethod
    def display_high_scores() -> None:
        
        Display.clear_screen()
        print("\n=== HIGH SCORES ===\n")
        
        try:
            with open("high_scores.json", 'r') as f:
                scores = json.load(f)
                
            if scores and isinstance(scores[0], int):
                new_scores = []
                for score in scores:
                    new_scores.append({
                        "player": "Anonymous",
                        "score": score,
                        "date": "Unknown"
                    })
                with open("high_scores.json", 'w') as f:
                    json.dump(new_scores, f, indent=2)
                scores = new_scores
                
            if not scores:
                print("No high scores yet!")
            else:
                for i, score_data in enumerate(scores[:10], 1):
                    print(f"{i}. {score_data['player']}: {score_data['score']} ({score_data['date']})")
        except (FileNotFoundError, json.JSONDecodeError):
            print("No high scores yet!")
        
        print("\nPress any key to continue...")
        InputHandler.wait_key()
    
    @staticmethod
    def display_settings_menu() -> None:
        
        settings = Settings()
        display = Display()
        while True:
            Display.clear_screen()
            print(f"\n{Fore.CYAN}=== USTAWIENIA ==={Style.RESET_ALL}")
            print(f"\n1. Rozmiar planszy (obecnie: {settings.get_board_size()}x{settings.get_board_size()})")
            print(f"2. Wartość docelowa (obecnie: {settings.get_target_value()})")
            print(f"3. Motyw kolorów (obecnie: {settings.get_color_theme()})")
            print("4. Dostosuj motyw")
            print("5. Statystyki")
            print("6. Powrót do menu głównego\n")
            
            choice = InputHandler.get_menu_input()
            
            if choice == 1:
                Display.clear_screen()
                print("\nWybierz rozmiar planszy:")
                print("1. 3x3")
                print("2. 4x4")
                print("3. 5x5")
                print("4. 6x6")
                size_choice = InputHandler.get_menu_input()
                if 1 <= size_choice <= 4:
                    settings.set_board_size(size_choice + 2)
            
            elif choice == 2:
                Display.clear_screen()
                print("\nWybierz wartość docelową:")
                print("1. 1024")
                print("2. 2048")
                print("3. 4096")
                value_choice = InputHandler.get_menu_input()
                if value_choice == 1:
                    settings.set_target_value(1024)
                elif value_choice == 2:
                    settings.set_target_value(2048)
                elif value_choice == 3:
                    settings.set_target_value(4096)
            
            elif choice == 3:
                Display.clear_screen()
                print("\nWybierz motyw kolorów:")
                themes = settings.get_available_themes()
                for i, theme in enumerate(themes, 1):
                    print(f"{i}. {theme}")
                theme_choice = InputHandler.get_menu_input()
                if 1 <= theme_choice <= len(themes):
                    settings.set_color_theme(themes[theme_choice - 1])
            
            elif choice == 4:
                display.display_theme_menu()
            
            elif choice == 5:
                Display.clear_screen()
                stats = Statistics()
                print(f"\n{Fore.CYAN}=== MENU STATYSTYK ==={Style.RESET_ALL}")
                print("\n1. Statystyki ogólne")
                print("2. Generuj wykresy")
                print("3. Eksportuj statystyki")
                print("4. Powrót\n")
                
                stats_choice = InputHandler.get_menu_input()
                if stats_choice == 1:
                    stats.display_historical_stats()
                    InputHandler.wait_key()
                elif stats_choice == 2:
                    stats.generate_plots()
                    print("\nWykresy zostały wygenerowane w katalogu 'stats'!")
                    InputHandler.wait_key()
                elif stats_choice == 3:
                    print("\nPodaj nazwę pliku do eksportu (domyślnie: game_statistics.txt):")
                    filename = InputHandler.get_text_input() or "game_statistics.txt"
                    stats.export_stats(filename)
                    print(f"\nStatystyki zostały wyeksportowane do pliku {filename}!")
                    InputHandler.wait_key()
            
            elif choice == 6:
                break
    
    def _check_autosave(self) -> None:
        
        now = datetime.now()
        if now - self.last_autosave >= self.autosave_interval:
            try:
                game_state = self.get_game_state()
                if self.save_manager.create_autosave(game_state):
                    self.last_autosave = now
            except Exception as e:
                self.error_handler.log_error(e, "Błąd podczas autozapisu")
    
    @classmethod
    def run_game(cls) -> None:

        while True:
            Display.clear_screen()
            print(f"\n{Fore.CYAN}=== 2048 ==={Style.RESET_ALL}")
            print("\n1. Nowa gra")
            print("2. Kontynuuj")
            print("3. Najlepsze wyniki")
            print("4. Ustawienia")
            print("5. Zapisy i checkpointy")
            print("6. Pomoc")
            print("7. Wyjście\n")
            
            choice = InputHandler.get_menu_input()
            
            if choice == 1:
                in_game_menu = True
                while in_game_menu:
                    Display.clear_screen()
                    print(f"\n{Fore.CYAN}=== MENU GIER ==={Style.RESET_ALL}")
                    print("\n1. Klasyczny")
                    print("2. Klasyczny z AI")
                    print("3. Czasowy")
                    print("4. Z przeszkodami")
                    print("5. Wyzwania")
                    print("6. Gra dwuosobowa")
                    print("7. Osiągnięcia")
                    print("8. Powrót\n")
                    
                    mode_choice = InputHandler.get_menu_input()
                    
                    if mode_choice == 8:
                        break
                    
                    elif mode_choice == 1:
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        player = Player(nickname)
                        game = cls(player=player)
                        game.run()
                        Display.clear_screen()
                    
                    elif mode_choice == 2:
                        from modes.classic_ai_mode import ClassicAIMode
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        player = Player(nickname)
                        ai_mode = ClassicAIMode()
                        ai_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 3:
                        from modes.time_mode import TimeMode
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        player = Player(nickname)
                        time_mode = TimeMode()
                        time_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 4:
                        from modes.obstacles_mode import ObstaclesMode
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        player = Player(nickname)
                        obstacles_mode = ObstaclesMode()
                        obstacles_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 5:
                        from modes.challenge_mode import ChallengeMode
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        player = Player(nickname)
                        
                        print(f"\n{Fore.CYAN}=== WYBIERZ WYZWANIE ==={Style.RESET_ALL}\n")
                        challenges = ChallengeMode.list_challenges()
                        for i, challenge in enumerate(challenges, 1):
                            print(f"{i}. {challenge}")
                        print(f"{len(challenges) + 1}. Powrót\n")
                        
                        challenge_choice = InputHandler.get_menu_input()
                        if 1 <= challenge_choice <= len(challenges):
                            challenge_mode = ChallengeMode(challenges[challenge_choice - 1])
                            challenge_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 6:
                        from modes.two_player_mode import TwoPlayerMode
                        Display.clear_screen()
                        print("\nPodaj nick pierwszego gracza: ")
                        nickname1 = InputHandler.get_text_input()
                        print("\nPodaj nick drugiego gracza: ")
                        nickname2 = InputHandler.get_text_input()
                        player1 = Player(nickname1)
                        player2 = Player(nickname2)
                        two_player_mode = TwoPlayerMode()
                        two_player_mode.run(player1, player2)
                        Display.clear_screen()
                    
                    elif mode_choice == 7:
                        Display.clear_screen()
                        print("\nPodaj swój nick: ")
                        nickname = InputHandler.get_text_input()
                        from core.achievements import Achievements
                        achievements = Achievements()
                        achievements.display_achievements(nickname)
                        InputHandler.wait_key()
                        Display.clear_screen()
            
            elif choice == 2:
                game = cls()
                if game.load_game():
                    game.run()
                else:
                    print("\nNie znaleziono zapisanej gry!")
                    InputHandler.wait_key()
            
            elif choice == 3:
                cls.display_high_scores()
                cls.display_settings_menu()
            
            elif choice == 5:
                game = cls()
                game.display_saves_menu()
            
            elif choice == 6:
                Display.display_controls()
                InputHandler.wait_key()
            
            elif choice == 7:
                Display.clear_screen()
                print("\nDziękujemy za grę!")
                os._exit(0)