import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
import os
import json

class DatabaseManager:
    
    def __init__(self, db_path: str = "game.db"):
        
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self) -> None:
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nickname TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    max_tile INTEGER DEFAULT 2,
                    moves INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    direction TEXT NOT NULL,
                    score_change INTEGER NOT NULL,
                    board_state TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
            """)
            
            conn.commit()
    
    def add_player(self, nickname: str) -> Optional[int]:
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO players (nickname) VALUES (?)",
                    (nickname,)
                )
                conn.commit()
                
                cursor.execute(
                    "SELECT id FROM players WHERE nickname = ?",
                    (nickname,)
                )
                result = cursor.fetchone()
                return result[0] if result else None
        except sqlite3.Error:
            return None
    
    def start_game(self, player_id: int, mode: str) -> Optional[int]:
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO games (player_id, mode) VALUES (?, ?)",
                    (player_id, mode)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error:
            return None
    
    def add_move(self, game_id: int, direction: str, score_change: int, board_state: List[List[int]]) -> bool:

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO moves (game_id, direction, score_change, board_state) VALUES (?, ?, ?, ?)",
                    (game_id, direction, score_change, json.dumps(board_state))
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def complete_game(self, game_id: int, final_score: int = None, max_tile: int = None) -> bool:
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                update_query = "UPDATE games SET completed_at = CURRENT_TIMESTAMP"
                params = []
                
                if final_score is not None:
                    update_query += ", score = ?"
                    params.append(final_score)
                
                if max_tile is not None:
                    update_query += ", max_tile = ?"
                    params.append(max_tile)
                
                update_query += " WHERE id = ?"
                params.append(game_id)
                
                cursor.execute(update_query, params)
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def get_high_scores(self, mode: str = None, limit: int = 10) -> List[Dict[str, Any]]:
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT 
                        p.nickname,
                        g.score,
                        g.max_tile,
                        g.moves,
                        g.mode,
                        g.started_at,
                        g.completed_at
                    FROM games g
                    JOIN players p ON p.id = g.player_id
                    WHERE g.completed_at IS NOT NULL
                """
                
                params = []
                if mode:
                    query += " AND g.mode = ?"
                    params.append(mode)
                
                query += " ORDER BY g.score DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'nickname': row[0],
                        'score': row[1],
                        'max_tile': row[2],
                        'moves': row[3],
                        'mode': row[4],
                        'started_at': row[5],
                        'completed_at': row[6]
                    })
                
                return results
        except sqlite3.Error:
            return [] 