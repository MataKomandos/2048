import os
import sys
import signal

def force_exit(signum, frame):
    print("\nDziękujemy za grę!")
    os._exit(0)

signal.signal(signal.SIGINT, force_exit)

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.game import Game

def main():
    try:
        game = Game()
        game.run_game()
    except KeyboardInterrupt:
        force_exit(None, None)
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 