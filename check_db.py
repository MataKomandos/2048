from core.database import DatabaseManager
import pandas as pd

def check_database():
    try:
        db = DatabaseManager("game_data.db")
        
        print("\n=== Wszyscy Gracze (SELECT * FROM players) ===")
        players = pd.read_sql("SELECT * FROM players", db.engine)
        print(players)
        
        print("\n=== Wszystkie Gry (SELECT * FROM games) ===")
        games = pd.read_sql("SELECT * FROM games", db.engine)
        print(games)
        
        print("\n=== Wszystkie Ruchy (SELECT * FROM moves) ===")
        moves = pd.read_sql("SELECT * FROM moves", db.engine)
        print(moves)
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

if __name__ == "__main__":
    check_database() 