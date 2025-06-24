#!/usr/bin/env python3
"""
Główny punkt wejścia do gry 2048.

Ten moduł inicjalizuje grę i obsługuje:
- Konfigurację ścieżek projektu
- Obsługę sygnałów (np. Ctrl+C)
- Uruchomienie głównej pętli gry
- Podstawową obsługę błędów
- Parsowanie argumentów wiersza poleceń
"""

import os
import sys
import signal
import argparse
from typing import Optional

def parse_arguments() -> argparse.Namespace:
    """
    Parsuje argumenty wiersza poleceń.
    
    Dostępne opcje:
    --mode: Tryb gry (classic, ai, time, obstacles, challenge, two_player)
    --size: Rozmiar planszy (3-6)
    --target: Wartość docelowa (1024, 2048, 4096)
    --load: Ścieżka do pliku z zapisaną grą
    --no-color: Wyłącz kolorowanie terminala
    --debug: Włącz tryb debugowania
    
    Returns:
        argparse.Namespace: Sparsowane argumenty
    """
    parser = argparse.ArgumentParser(
        description="Gra logiczna 2048 - łącz kafelki, aby osiągnąć 2048!",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode',
        choices=['classic', 'ai', 'time', 'obstacles', 'challenge', 'two_player'],
        default='classic',
        help='Tryb gry (domyślnie: classic)'
    )
    
    parser.add_argument(
        '--size',
        type=int,
        choices=range(3, 7),
        default=4,
        help='Rozmiar planszy NxN (domyślnie: 4)'
    )
    
    parser.add_argument(
        '--target',
        type=int,
        choices=[1024, 2048, 4096],
        default=2048,
        help='Wartość docelowa do wygrania (domyślnie: 2048)'
    )
    
    parser.add_argument(
        '--load',
        type=str,
        help='Wczytaj zapisaną grę z podanego pliku'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Wyłącz kolorowanie terminala'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Włącz tryb debugowania'
    )
    
    return parser.parse_args()

def force_exit(signum, frame):
    """
    Wymusza bezpieczne zakończenie programu.
    
    Wywoływane przy:
    - Naciśnięciu Ctrl+C
    - Otrzymaniu sygnału SIGINT
    - Zamknięciu okna terminala
    """
    print("\nDziękujemy za grę!")
    os._exit(0)

# Rejestruj handler dla Ctrl+C
signal.signal(signal.SIGINT, force_exit)

# Dodaj katalog główny projektu do ścieżki Pythona
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importuj grę
from core.game import Game
from core.settings import Settings

def validate_load_file(filepath: str) -> bool:
    """
    Sprawdza czy plik z zapisem gry istnieje i jest poprawny.
    
    Args:
        filepath (str): Ścieżka do pliku
        
    Returns:
        bool: True jeśli plik jest poprawny
    """
    if not os.path.exists(filepath):
        print(f"Błąd: Plik {filepath} nie istnieje")
        return False
    
    if not os.path.isfile(filepath):
        print(f"Błąd: {filepath} nie jest plikiem")
        return False
    
    if not filepath.endswith(('.json', '.2048')):
        print(f"Błąd: {filepath} ma nieprawidłowe rozszerzenie (wymagane .json lub .2048)")
        return False
    
    return True

def main():
    """
    Uruchamia grę i obsługuje podstawowe błędy.
    
    Obsługiwane sytuacje:
    - Normalne uruchomienie gry
    - Przerwanie przez użytkownika (Ctrl+C)
    - Nieoczekiwane błędy
    - Nieprawidłowe argumenty
    """
    try:
        args = parse_arguments()
        
        # Konfiguracja na podstawie argumentów
        settings = Settings()
        settings.set_board_size(args.size)
        settings.set_target_value(args.target)
        if args.no_color:
            settings.set_use_colors(False)
        if args.debug:
            settings.set_debug_mode(True)
        
        game = Game(size=args.size)
        
        # Wczytaj zapisaną grę jeśli podano
        if args.load:
            if validate_load_file(args.load):
                if not game.load_game(args.load):
                    print(f"Błąd: Nie udało się wczytać gry z pliku {args.load}")
                    sys.exit(1)
            else:
                sys.exit(1)
        
        # Uruchom odpowiedni tryb gry
        if args.mode == 'classic':
            game.run_game()
        elif args.mode == 'ai':
            from modes.classic_ai_mode import ClassicAIMode
            ai_mode = ClassicAIMode()
            ai_mode.run(None)  # None jako player, bo nie potrzebujemy nicku w trybie AI
        elif args.mode == 'time':
            from modes.time_mode import TimeMode
            time_mode = TimeMode()
            time_mode.run(None)
        elif args.mode == 'obstacles':
            from modes.obstacles_mode import ObstaclesMode
            obstacles_mode = ObstaclesMode()
            obstacles_mode.run(None)
        elif args.mode == 'challenge':
            from modes.challenge_mode import ChallengeMode
            challenge_mode = ChallengeMode()
            challenge_mode.run(None)
        elif args.mode == 'two_player':
            from modes.two_player_mode import TwoPlayerMode
            two_player_mode = TwoPlayerMode()
            two_player_mode.run(None, None)  # Nicki graczy będą pobrane w trybie
            
    except KeyboardInterrupt:
        force_exit(None, None)
    except Exception as e:
        if args.debug:
            import traceback
            print(f"\nWystąpił błąd:\n{traceback.format_exc()}")
        else:
            print(f"\nWystąpił błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 