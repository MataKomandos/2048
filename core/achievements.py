import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from colorama import Fore, Style

class Achievements:
    ACHIEVEMENTS = {
        "first_win": {
            "name": "Pierwsze zwycięstwo",
            "description": "Osiągnij kafelek 2048 po raz pierwszy",
            "points": 100
        },
        "speed_demon": {
            "name": "Szybki jak błyskawica",
            "description": "Ukończ grę w trybie czasowym w mniej niż 5 minut",
            "points": 200
        },
        "obstacle_master": {
            "name": "Mistrz przeszkód",
            "description": "Wygraj grę w trybie z przeszkodami",
            "points": 150
        },
        "symmetry_keeper": {
            "name": "Strażnik symetrii",
            "description": "Ukończ wyzwanie 'Symetria'",
            "points": 150
        },
        "tower_builder": {
            "name": "Budowniczy wieży",
            "description": "Ukończ wyzwanie 'Wieża'",
            "points": 200
        },
        "spiral_master": {
            "name": "Mistrz spirali",
            "description": "Ukończ wyzwanie 'Spirala'",
            "points": 150
        },
        "team_player": {
            "name": "Gracz zespołowy",
            "description": "Wygraj grę w trybie dwuosobowym",
            "points": 100
        },
        "high_score": {
            "name": "Rekordowy wynik",
            "description": "Zdobądź ponad 20000 punktów",
            "points": 250
        }
    }
    
    def __init__(self):
        self.achievements_file = "achievements.json"
        self.player_achievements = {}
        self._load_achievements()
    
    def _load_achievements(self) -> None:
        try:
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, 'r', encoding='utf-8') as f:
                    self.player_achievements = json.load(f)
        except Exception as e:
            print(f"Błąd podczas wczytywania osiągnięć: {e}")
            self.player_achievements = {}
    
    def _save_achievements(self) -> None:
        try:
            with open(self.achievements_file, 'w', encoding='utf-8') as f:
                json.dump(self.player_achievements, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd podczas zapisywania osiągnięć: {e}")
    
    def unlock_achievement(self, player_nickname: str, achievement_id: str) -> bool:
        if achievement_id not in self.ACHIEVEMENTS:
            return False
        
        if player_nickname not in self.player_achievements:
            self.player_achievements[player_nickname] = []
        
        if achievement_id not in self.player_achievements[player_nickname]:
            self.player_achievements[player_nickname].append(achievement_id)
            self._save_achievements()
            return True
        
        return False
    
    def display_achievements(self, player_nickname: str) -> None:
        print(f"\n{Fore.CYAN}=== OSIĄGNIĘCIA GRACZA {player_nickname} ==={Style.RESET_ALL}\n")
        
        player_achievements = self.player_achievements.get(player_nickname, [])
        total_points = 0
        
        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            unlocked = achievement_id in player_achievements
            color = Fore.GREEN if unlocked else Fore.RED
            status = "✓" if unlocked else "✗"
            
            print(f"{color}{status} {achievement['name']}{Style.RESET_ALL}")
            print(f"   {achievement['description']}")
            print(f"   Punkty: {achievement['points']}\n")
            
            if unlocked:
                total_points += achievement['points']
        
        print(f"\nŁączna liczba punktów: {Fore.YELLOW}{total_points}{Style.RESET_ALL}")
    
    def get_player_points(self, player_nickname: str) -> int:
        player_achievements = self.player_achievements.get(player_nickname, [])
        return sum(self.ACHIEVEMENTS[ach_id]['points'] for ach_id in player_achievements)
    
    def check_game_achievements(self, player_nickname: str, game_data: Dict) -> List[str]:  
        unlocked = []
        
        if game_data.get("won", False):
            if self.unlock_achievement(player_nickname, "first_win"):
                unlocked.append("first_win")
        
        if game_data.get("score", 0) > 20000:
            if self.unlock_achievement(player_nickname, "high_score"):
                unlocked.append("high_score")
        
        game_mode = game_data.get("mode")
        if game_mode == "time" and game_data.get("time", 0) < 300:  # 5 minut
            if self.unlock_achievement(player_nickname, "speed_demon"):
                unlocked.append("speed_demon")
        
        elif game_mode == "obstacles" and game_data.get("won", False):
            if self.unlock_achievement(player_nickname, "obstacle_master"):
                unlocked.append("obstacle_master")
        
        elif game_mode == "challenge":
            challenge_name = game_data.get("challenge_name")
            if challenge_name == "Symetria" and game_data.get("completed", False):
                if self.unlock_achievement(player_nickname, "symmetry_keeper"):
                    unlocked.append("symmetry_keeper")
            elif challenge_name == "Wieża" and game_data.get("completed", False):
                if self.unlock_achievement(player_nickname, "tower_builder"):
                    unlocked.append("tower_builder")
            elif challenge_name == "Spirala" and game_data.get("completed", False):
                if self.unlock_achievement(player_nickname, "spiral_master"):
                    unlocked.append("spiral_master")
        
        elif game_mode == "two_player" and game_data.get("won", False):
            if self.unlock_achievement(player_nickname, "team_player"):
                unlocked.append("team_player")
        
        return unlocked
    
    def display_unlocked_achievements(self, unlocked: List[str]) -> None:
        if unlocked:
            print(f"\n{Fore.YELLOW}Nowe osiągnięcia!{Style.RESET_ALL}")
            for achievement_id in unlocked:
                achievement = self.ACHIEVEMENTS[achievement_id]
                print(f"\n{Fore.GREEN}✓ {achievement['name']}{Style.RESET_ALL}")
                print(f"   {achievement['description']}")
                print(f"   +{achievement['points']} punktów") 