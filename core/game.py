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
    """
    Główna klasa gry 2048 zarządzająca logiką i przebiegiem rozgrywki.
    
    Klasa odpowiada za:
    - Inicjalizację i zarządzanie stanem gry
    - Obsługę ruchów gracza
    - Zapisywanie i wczytywanie stanu gry
    - Zarządzanie punktacją i postępem
    - Interakcję z bazą danych
    - Automatyczne zapisywanie
    """
    
    def __init__(self, size: int = None, player: Optional[Player] = None):
        """
        Inicjalizacja nowej gry.
        
        Args:
            size (int, optional): Rozmiar planszy. Jeśli nie podano, używany jest rozmiar z ustawień.
            player (Player, optional): Obiekt gracza. Jeśli podano, gra jest zapisywana w bazie danych.
        """
        self.settings = Settings()
        self.save_manager = SaveManager()
        self.db_manager = DatabaseManager()  # Initialize database manager
        self.board = Board(size if size else self.settings.get_board_size())
        self.running = True
        self.won = False
        self.player = player
        self.needs_redraw = True
        self.statistics = Statistics()  # Initialize statistics
        self.error_handler = ErrorHandler()
        self.last_autosave = datetime.now()
        self.autosave_interval = timedelta(minutes=5)  # Autozapis co 5 minut
        self.db_game = None  # Reference to the current game in database
        
        # Obsługa sygnałów przerwania
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

        # If player is provided, create or get from database
        if self.player:
            self.db_player = self.db_manager.add_player(self.player.nickname)
            self.db_game = self.db_manager.start_game(self.db_player, "classic")
    
    def _handle_interrupt(self, signum, frame):
        """
        Obsługa przerwania gry (Ctrl+C, zamknięcie okna).
        
        Zapisuje stan gry przed zamknięciem.
        """
        print("\nPrzechwycono sygnał przerwania. Zapisywanie stanu gry...")
        self._emergency_save()
        sys.exit(0)
    
    def _emergency_save(self) -> None:
        """Awaryjny zapis stanu gry."""
        if self.board and self.player:
            try:
                game_state = self.get_game_state()
                self.save_manager.create_autosave(game_state)
                print("Stan gry został zapisany.")
            except Exception as e:
                self.error_handler.log_error(e, "Błąd podczas awaryjnego zapisu")
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Pobiera aktualny stan gry do zapisania.
        
        Returns:
            Dict[str, Any]: Słownik zawierający:
                - board: Aktualny stan planszy
                - score: Aktualny wynik
                - size: Rozmiar planszy
                - won: Czy gra została wygrana
                - player_nickname: Nick gracza (jeśli istnieje)
                - settings: Aktualne ustawienia
                - timestamp: Znacznik czasu
        """
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
        """
        Wczytuje zapisany stan gry.
        
        Args:
            state (Dict[str, Any]): Stan gry do wczytania zawierający wszystkie
                                   niezbędne informacje (plansza, wynik, ustawienia itp.)
        """
        self.board = Board(state["size"])
        self.board.board = state["board"]
        self.board.score = state["score"]
        self.won = state["won"]
        if state["player_nickname"]:
            self.player = Player(state["player_nickname"])
        if "settings" in state:
            self.settings.settings = state["settings"]
            self.settings.save_settings()
        self.running = True  # Upewnij się, że gra jest aktywna
        self.needs_redraw = True  # Wymuś przerysowanie planszy przez zmiane danych
        self.last_autosave = datetime.fromisoformat(state["timestamp"])
    
    def save_game(self, filename: str = "save_game.json") -> bool:
        """Save current game state."""
        try:
            game_state = self.get_game_state()
            return self.save_manager.save_game(game_state, filename)
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas zapisywania gry")
            return False
    
    def load_game(self, filename: str = "save_game.json") -> bool:
        """Load game state from file."""
        try:
            state = self.save_manager.load_game(filename)
            if state:
                self.load_game_state(state) #jeśli zostało wczytane odtwarza stan
                return True
            return False #jesli load_game nie zwróciło
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas wczytywania gry")
            return False
    
    def create_checkpoint(self, name: Optional[str] = None) -> str:
        """Create a checkpoint of current game state."""
        return self.save_manager.create_checkpoint(self.get_game_state(), name)
    
    def load_checkpoint(self, filename: str) -> bool:
        """Load a checkpoint file.
        
        Args:
            filename (str): Name of the checkpoint file
        
        Returns:
            bool: True if checkpoint was loaded successfully
        """
        game_data = self.save_manager.load_checkpoint(filename)
        if game_data:
            self.load_game_state(game_data)
            return True  #jeśli odczyta odtwarza stan
        return False
    
    def export_game(self, filepath: str) -> bool:
        """Export game to file."""
        return self.save_manager.export_game(self.get_game_state(), filepath)
    
    def import_game(self, filepath: str) -> bool:
        """Import game from file."""
        state = self.save_manager.import_game(filepath)
        if state:
            self.load_game_state(state)
            return True
        return False
    
    @staticmethod
    def display_saves_menu() -> None:
        """Wyświetla menu zapisów i checkpointów."""
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
        """Wyświetla menu wczytywania zapisów."""
        Display.clear_screen()
        print("\n=== WCZYTYWANIE ZAPISU ===\n")
        print("Dostępne zapisy:\n")
        
        save_manager = SaveManager()
        saves = save_manager.list_saves()
        
        if not saves:
            print("Brak dostępnych zapisów!")
            InputHandler.wait_key()
            return
            
        for i, save in enumerate(saves, 1):    #numeruje od 1
            timestamp = datetime.fromisoformat(save['timestamp']).strftime("%Y-%m-%d %H:%M:%S") #format
            print(f"{i}. {save['name']} (Wynik: {save['score']}, Data: {timestamp})") #lista zapisów
        
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
        """Menu tworzenia checkpointu."""
        Display.clear_screen()
        print("\n=== TWORZENIE CHECKPOINTU ===\n")
        print("Podaj nazwę checkpointu (lub zostaw puste dla automatycznej nazwy):")
        name = InputHandler.get_text_input(allow_empty=True) #pozwala zostwić puste pole
        
        save_manager = SaveManager()
        game = Game()  # Temporary game instance to get current state
        
        checkpoint_name = save_manager.create_checkpoint(game.get_game_state(), name if name else None)
        
        if checkpoint_name:
            print(f"\nCheckpoint '{checkpoint_name}' został utworzony!")
        else:
            print("\nBłąd podczas tworzenia checkpointu!")
        InputHandler.wait_key()

    @staticmethod
    def _load_checkpoint_menu() -> None:
        """Menu wczytywania checkpointu."""
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
        game = Game()  # Temporary game instance
        
        if game.load_checkpoint(selected_checkpoint):
            print("\nCheckpoint został wczytany pomyślnie!")
        else:
            print("\nBłąd podczas wczytywania checkpointu!")
        InputHandler.wait_key()

    @staticmethod
    def _export_game_menu() -> None:
        """Menu eksportu gry."""
        Display.clear_screen()
        print("\n=== EKSPORT GRY ===\n")
        print("Podaj nazwę pliku eksportu (bez rozszerzenia):")
        filename = InputHandler.get_text_input()
        
        if not filename:
            return
            
        filepath = f"{filename}.2048"
        game = Game()  # Temporary game instance
        
        if game.export_game(filepath):
            print(f"\nGra została wyeksportowana do pliku: {filepath}")
        else:
            print("\nBłąd podczas eksportu gry!")
        InputHandler.wait_key()

    @staticmethod
    def _import_game_menu() -> None:
        """Menu importu gry."""
        Display.clear_screen()
        print("\n=== IMPORT GRY ===\n")
        print("Podaj nazwę pliku do importu (bez rozszerzenia):")
        filename = InputHandler.get_text_input()
        
        if not filename:
            return
            
        filepath = f"{filename}.2048"
        game = Game()  # Temporary game instance
        
        if game.import_game(filepath):
            print("\nGra została zaimportowana pomyślnie!")
        else:
            print("\nBłąd podczas importu gry!")
        InputHandler.wait_key()
    
    def run(self) -> None:
        """
        Główna pętla gry.
        
        Odpowiada za:
        - Wyświetlanie planszy
        - Obsługę komend gracza
        - Sprawdzanie warunków końca gry
        - Automatyczne zapisywanie
        - Obsługę błędów
        """
        try:
            Display.clear_screen()
            self.needs_redraw = True
            
            while self.running:
                if self.needs_redraw:
                    difficulty = self.board.calculate_difficulty()
                    Display.display_board( #aktualna plansza
                        self.board.get_board(),
                        self.board.get_score(),
                        self.player.nickname if self.player else None,
                        self.settings.get_theme_colors(),
                        difficulty,
                        self.board.can_undo(),
                        self.board.get_remaining_undos()
                    )
                    self.needs_redraw = False
                
                if self.board.is_game_over(): #czy gra sie zakonczyła
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
                    Display.display_game_over(self.board.get_score()) #pokazuje koniec z wynikiem
                    if self.db_game:
                        self.db_manager.complete_game(self.db_game)
                    self.statistics.end_session()  # Save session stats
                    self.statistics.display_session_stats()  # statystyki po zakonczeniu gry
                    if self.player:
                        self.player.save_score(self.board.get_score())
                    self.running = False
                    InputHandler.wait_key()
                    break
                
                if not self.won and self.board.has_won():#sprawdzenie wygranej
                    self.won = True
                    Display.display_win(self.board.get_score())
                    InputHandler.wait_key()
                    self.needs_redraw = True
                
                # Get and process input
                command = InputHandler.get_input()
                if command:
                    self.process_command(command)
                
                # Small delay to prevent CPU overuse
                time.sleep(0.01)
                
                # Sprawdzenie czy należy wykonać automatyczny zapis
                self._check_autosave()
            
        except Exception as e:
            self.error_handler.log_error(e, "Krytyczny błąd w głównej pętli gry")
            self._emergency_save()
        finally:
            # Zawsze próbuj zapisać stan gry przed zakończeniem
            self._emergency_save()
    
    def process_command(self, command: str) -> None:
        """
        Przetwarza komendy gracza.
        
        Args:
            command (str): Komenda do przetworzenia. Możliwe wartości:
                - 'quit': Wyjście z gry
                - 'restart': Restart gry
                - 'help': Wyświetlenie pomocy
                - 'undo': Cofnięcie ruchu
                - 'up', 'down', 'left', 'right': Ruchy na planszy
        """
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
        """Display high scores for all players."""
        Display.clear_screen()
        print("\n=== HIGH SCORES ===\n")
        
        try:
            with open("high_scores.json", 'r') as f:
                scores = json.load(f)
                
            # Convert old format to new if needed
            if scores and isinstance(scores[0], int):
                # Convert old format to new format
                new_scores = []
                for score in scores:
                    new_scores.append({
                        "player": "Anonymous",
                        "score": score,
                        "date": "Unknown"
                    })
                # Save in new format
                with open("high_scores.json", 'w') as f:
                    json.dump(new_scores, f, indent=2)
                scores = new_scores
                
            if not scores:
                print("Nie ma jeszcze żadnych wyników!")
            else:
                for i, score_data in enumerate(scores[:10], 1):
                    print(f"{i}. {score_data['player']}: {score_data['score']} ({score_data['date']})")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Nie ma jeszcze żadnych wyników!")
        
        print("\nPress any key to continue...")
        InputHandler.wait_key()
    
    @staticmethod
    def display_settings_menu() -> None:
        """Wyświetla menu ustawień."""
        settings = Settings()
        display = Display()
        while True:
            Display.clear_screen()
            print(f"\n{Fore.CYAN}=== USTAWIENIA ==={Style.RESET_ALL}")
            print(f"\n1. Rozmiar planszy (obecnie: {settings.get_board_size()}x{settings.get_board_size()})")
            print(f"2. Wartość docelowa (obecnie: {settings.get_target_value()})")
            print("3. Dostosuj motyw")
            print("4. Statystyki")
            print("5. Powrót do menu głównego\n")
            
            choice = InputHandler.get_menu_input()
            
            if choice == 1:  # Rozmiar planszy
                Display.clear_screen()
                print("\nWybierz rozmiar planszy:")
                print("1. 3x3")
                print("2. 4x4")
                print("3. 5x5")
                print("4. 6x6")
                size_choice = InputHandler.get_menu_input()
                if 1 <= size_choice <= 4:
                    settings.set_board_size(size_choice + 2)
            
            elif choice == 2:  # Wartość docelowa
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
            
            elif choice == 3:  # Dostosuj motyw
                display.display_theme_menu()
            
            elif choice == 4:  # Statystyki
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
            
            elif choice == 5:  # Powrót
                break
    
    def _check_autosave(self) -> None:
        """Sprawdza czy należy wykonać automatyczny zapis."""
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
        """Main entry point for the game."""
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
            
            if choice == 1:  # Nowa gra - wybór trybu
                Display.clear_screen()
                print("\nPodaj swój nick: ")
                nickname = InputHandler.get_text_input()
                if not nickname:  # Jeśli użytkownik nie podał nicku
                    continue
                
                player = Player(nickname)
                
                in_game_menu = True
                while in_game_menu:
                    Display.clear_screen()
                    print(f"\n{Fore.CYAN}=== MENU GIER ==={Style.RESET_ALL}")
                    print(f"\nGracz: {nickname}")  # Pokazujemy nick gracza
                    print("\n1. Klasyczny")
                    print("2. Klasyczny z AI")
                    print("3. Czasowy")
                    print("4. Z przeszkodami")
                    print("5. Wyzwania")
                    print("6. Gra dwuosobowa")
                    print("7. Osiągnięcia")
                    print("8. Powrót\n")
                    
                    mode_choice = InputHandler.get_menu_input()
                    
                    if mode_choice == 8:  # Powrót do głównego menu
                        break  # Wyjście z pętli menu gier
                    
                    # Obsługa pozostałych opcji menu gier
                    elif mode_choice == 1:  # Klasyczny
                        game = cls(player=player)
                        game.run()
                        Display.clear_screen()
                    
                    elif mode_choice == 2:  # Klasyczny z AI
                        from modes.classic_ai_mode import ClassicAIMode
                        ai_mode = ClassicAIMode()
                        ai_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 3:  # Czasowy
                        from modes.time_mode import TimeMode
                        time_mode = TimeMode()
                        time_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 4:  # Z przeszkodami
                        from modes.obstacles_mode import ObstaclesMode
                        obstacles_mode = ObstaclesMode()
                        obstacles_mode.run(player)
                        Display.clear_screen()
                    
                    elif mode_choice == 5:  # Wyzwania
                        from modes.challenge_mode import ChallengeMode
                        Display.clear_screen()
                        
                        # Wybór wyzwania
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
                    
                    elif mode_choice == 6:  # Gra dwuosobowa
                        from modes.two_player_mode import TwoPlayerMode
                        Display.clear_screen()
                        print("\nPodaj nick drugiego gracza: ")
                        nickname2 = InputHandler.get_text_input()
                        player2 = Player(nickname2)
                        two_player_mode = TwoPlayerMode()
                        two_player_mode.run(player, player2)
                        Display.clear_screen()
                    
                    elif mode_choice == 7:  # Osiągnięcia
                        from core.achievements import Achievements
                        achievements = Achievements()
                        achievements.display_achievements(nickname)
                        InputHandler.wait_key()
                        Display.clear_screen()
            
            elif choice == 2:  # Kontynuuj
                game = cls()
                if game.load_game():
                    game.run()
                else:
                    print("\nNie znaleziono zapisanej gry!")
                    InputHandler.wait_key()
            
            elif choice == 3:  # Najlepsze wyniki
                cls.display_high_scores()
            
            elif choice == 4:  # Ustawienia
                cls.display_settings_menu()
            
            elif choice == 5:  # Zapisy i checkpointy
                game = cls()
                game.display_saves_menu()
            
            elif choice == 6:  # Pomoc
                Display.display_controls()
                InputHandler.wait_key()
            
            elif choice == 7:  # Wyjście
                Display.clear_screen()
                print("\nDziękujemy za grę!")
                os._exit(0)