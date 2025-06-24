import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class Player:
    """Class handling player data and scores."""
    
    def __init__(self, nickname: str):
        """Initialize player with nickname."""
        self.nickname = nickname
        self.scores_file = "high_scores.json"
    
    def save_score(self, score: int) -> None:
        """Save player's score to high scores file."""
        try:
            with open(self.scores_file, 'r') as f:
                all_scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            all_scores = []
            
        # Add new score with timestamp
        score_entry = {
            "player": self.nickname,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        all_scores.append(score_entry)
        
        # Sort by score (descending)
        all_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Save all scores
        with open(self.scores_file, 'w') as f:
            json.dump(all_scores, f, indent=2)
    
    def get_scores(self) -> List[Dict[str, any]]:
        """Get all scores for this player."""
        try:
            with open(self.scores_file, 'r') as f:
                all_scores = json.load(f)
                return [score for score in all_scores if score["player"] == self.nickname]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def get_top_scores() -> List[Dict[str, any]]:
        """Get top 10 scores across all players."""
        try:
            with open("high_scores.json", 'r') as f:
                all_scores = json.load(f)
                return all_scores[:10]  # Return top 10 scores (already sorted)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] 