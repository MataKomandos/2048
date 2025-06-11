from typing import Dict, List, Optional
import json
import time
from datetime import datetime
import os
import matplotlib.pyplot as plt
from colorama import Fore, Style

class Statistics:
    
    def __init__(self):
        self.stats_file = "game_stats.json"
        self.current_session = {
            "start_time": time.time(),
            "moves": 0,
            "moves_by_direction": {
                "up": 0,
                "down": 0,
                "left": 0,
                "right": 0
            },
            "merges": 0,
            "max_tile": 0,
            "score": 0,
            "tile_distribution": {},
            "game_duration": 0
        }
        self.load_stats()
    
    def load_stats(self) -> None:
        try:
            with open(self.stats_file, 'r') as f:
                self.historical_stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.historical_stats = {
                "games_played": 0,
                "total_moves": 0,
                "highest_score": 0,
                "best_tile": 0,
                "total_time_played": 0,
                "moves_history": [],
                "scores_history": [],
                "max_tiles_history": [],
                "direction_stats": {
                    "up": 0,
                    "down": 0,
                    "left": 0,
                    "right": 0
                }
            }
    
    def save_stats(self) -> None:
        with open(self.stats_file, 'w') as f:
            json.dump(self.historical_stats, f, indent=2)
    
    def update_move_stats(self, direction: str, board: List[List[int]], score: int) -> None:

        self.current_session["moves"] += 1
        self.current_session["moves_by_direction"][direction] += 1
        self.current_session["score"] = score
        
        tile_counts = {}
        max_tile = 0
        for row in board:
            for tile in row:
                if tile > 0:
                    tile_counts[str(tile)] = tile_counts.get(str(tile), 0) + 1
                    max_tile = max(max_tile, tile)
        
        self.current_session["tile_distribution"] = tile_counts
        self.current_session["max_tile"] = max(self.current_session["max_tile"], max_tile)
    
    def end_session(self) -> None:

        self.current_session["game_duration"] = time.time() - self.current_session["start_time"]
        
        self.historical_stats["games_played"] += 1
        self.historical_stats["total_moves"] += self.current_session["moves"]
        self.historical_stats["highest_score"] = max(
            self.historical_stats["highest_score"],
            self.current_session["score"]
        )
        self.historical_stats["best_tile"] = max(
            self.historical_stats["best_tile"],
            self.current_session["max_tile"]
        )
        self.historical_stats["total_time_played"] += self.current_session["game_duration"]
        
        self.historical_stats["moves_history"].append(self.current_session["moves"])
        self.historical_stats["scores_history"].append(self.current_session["score"])
        self.historical_stats["max_tiles_history"].append(self.current_session["max_tile"])

        for direction, count in self.current_session["moves_by_direction"].items():
            self.historical_stats["direction_stats"][direction] += count
        
        self.save_stats()
    
    def display_session_stats(self) -> None:

        duration = time.time() - self.current_session["start_time"]
        
        print(f"\n{Fore.CYAN}=== STATYSTYKI SESJI ==={Style.RESET_ALL}")
        print(f"\nCzas gry: {int(duration)} sekund")
        print(f"Liczba ruchów: {self.current_session['moves']}")
        print(f"Największy blok: {self.current_session['max_tile']}")
        print(f"Wynik: {self.current_session['score']}")
        
        print("\nRuchy według kierunków:")
        for direction, count in self.current_session["moves_by_direction"].items():
            print(f"{direction}: {count}")
        
        print("\nRozkład bloków:")
        for value, count in sorted(self.current_session["tile_distribution"].items(),
                                 key=lambda x: int(x[0])):
            print(f"{value}: {count}")
    
    def display_historical_stats(self) -> None:

        print(f"\n{Fore.CYAN}=== STATYSTYKI OGÓLNE ==={Style.RESET_ALL}")
        print(f"\nRozegrane gry: {self.historical_stats['games_played']}")
        print(f"Całkowita liczba ruchów: {self.historical_stats['total_moves']}")
        print(f"Najwyższy wynik: {self.historical_stats['highest_score']}")
        print(f"Najwyższy blok: {self.historical_stats['best_tile']}")
        
        total_time = self.historical_stats['total_time_played']
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        print(f"Całkowity czas gry: {hours}h {minutes}m")
        
        if self.historical_stats['games_played'] > 0:
            avg_moves = self.historical_stats['total_moves'] / self.historical_stats['games_played']
            print(f"\nŚrednia liczba ruchów na grę: {avg_moves:.1f}")
        
        print("\nStatystyki kierunków:")
        total_moves = sum(self.historical_stats["direction_stats"].values())
        if total_moves > 0:
            for direction, count in self.historical_stats["direction_stats"].items():
                percentage = (count / total_moves) * 100
                print(f"{direction}: {count} ({percentage:.1f}%)")
    
    def generate_plots(self) -> None:

        if not os.path.exists('stats'):
            os.makedirs('stats')
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.historical_stats["scores_history"], marker='o')
        plt.title("Postęp wyników")
        plt.xlabel("Numer gry")
        plt.ylabel("Wynik")
        plt.grid(True)
        plt.savefig('stats/scores_progress.png')
        plt.close()
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.historical_stats["max_tiles_history"], marker='o', color='green')
        plt.title("Największe osiągnięte bloki")
        plt.xlabel("Numer gry")
        plt.ylabel("Wartość bloku")
        plt.grid(True)
        plt.savefig('stats/max_tiles_progress.png')
        plt.close()
        
        plt.figure(figsize=(8, 8))
        directions = self.historical_stats["direction_stats"]
        plt.pie(directions.values(), labels=directions.keys(), autopct='%1.1f%%')
        plt.title("Rozkład kierunków ruchu")
        plt.savefig('stats/direction_distribution.png')
        plt.close()
    
    def export_stats(self, filename: str = "game_statistics.txt") -> None:
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== STATYSTYKI GRY 2048 ===\n\n")
            f.write(f"Data eksportu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("OGÓLNE STATYSTYKI:\n")
            f.write(f"Rozegrane gry: {self.historical_stats['games_played']}\n")
            f.write(f"Całkowita liczba ruchów: {self.historical_stats['total_moves']}\n")
            f.write(f"Najwyższy wynik: {self.historical_stats['highest_score']}\n")
            f.write(f"Najwyższy blok: {self.historical_stats['best_tile']}\n")
            
            total_time = self.historical_stats['total_time_played']
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            f.write(f"Całkowity czas gry: {hours}h {minutes}m\n\n")
            
            f.write("STATYSTYKI KIERUNKÓW:\n")
            total_moves = sum(self.historical_stats["direction_stats"].values())
            for direction, count in self.historical_stats["direction_stats"].items():
                percentage = (count / total_moves) * 100 if total_moves > 0 else 0
                f.write(f"{direction}: {count} ({percentage:.1f}%)\n")
            
            f.write("\nHISTORIA WYNIKÓW:\n")
            for i, score in enumerate(self.historical_stats["scores_history"], 1):
                f.write(f"Gra {i}: {score}\n")
            
            f.write("\nHISTORIA NAJWIĘKSZYCH BLOKÓW:\n")
            for i, tile in enumerate(self.historical_stats["max_tiles_history"], 1):
                f.write(f"Gra {i}: {tile}\n") 