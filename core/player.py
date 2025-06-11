import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class Player:
    
    def __init__(self, nickname: str):
        self.nickname = nickname
        self.scores_file = "high_scores.json"
    
    def save_score(self, score: int) -> None:
        try:
            with open(self.scores_file, 'r') as f:
                all_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_scores = []
            
        score_entry = {
            "player": self.nickname,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        all_scores.append(score_entry)
        
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        
        with open(self.scores_file, 'w') as f:
            json.dump(all_scores, f, indent=2)
    
    def get_scores(self) -> List[Dict[str, any]]:
        try:
            with open(self.scores_file, 'r') as f:
                all_scores = json.load(f)
                return [score for score in all_scores if score["player"] == self.nickname]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def get_top_scores() -> List[Dict[str, any]]:
        try:
            with open("high_scores.json", 'r') as f:
                all_scores = json.load(f)
                return all_scores[:10]
        except (FileNotFoundError, json.JSONDecodeError):
            return [] 