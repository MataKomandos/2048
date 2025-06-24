from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import List, Optional
import os

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    nickname = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    games = relationship("Game", back_populates="player")
    
class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    score = Column(Integer, default=0)
    max_tile = Column(Integer, default=2)
    moves_count = Column(Integer, default=0)
    duration = Column(Float)  # in seconds
    game_mode = Column(String(20))
    completed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    
    player = relationship("Player", back_populates="games")
    moves = relationship("Move", back_populates="game")

class Move(Base):
    __tablename__ = 'moves'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    direction = Column(String(10))
    score_change = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.now)
    
    game = relationship("Game", back_populates="moves")

class DatabaseManager:
    def __init__(self, db_path: str = "game_data.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_player(self, nickname: str) -> Player:
        """Dodaj nowego gracza lub zwróć istniejącego."""
        player = self.session.query(Player).filter_by(nickname=nickname).first()
        if not player:
            player = Player(nickname=nickname)
            self.session.add(player)
            self.session.commit()
        return player
    
    def start_game(self, player: Player, game_mode: str) -> Game:
        """Rozpocznij nową grę."""
        game = Game(player=player, game_mode=game_mode)
        self.session.add(game)
        self.session.commit()
        return game
    
    def add_move(self, game: Game, direction: str, score_change: int) -> None:
        """Zapisz ruch w grze."""
        move = Move(game=game, direction=direction, score_change=score_change)
        self.session.add(move)
        game.moves_count += 1
        self.session.commit()
    
    def update_game(self, game: Game, score: int, max_tile: int) -> None:
        """Aktualizuj statystyki gry."""
        game.score = score
        game.max_tile = max_tile
        self.session.commit()
    
    def complete_game(self, game: Game) -> None:
        """Zakończ grę."""
        game.completed = datetime.now()
        game.duration = (game.completed - game.created_at).total_seconds()
        self.session.commit()
    
    def get_player_stats(self, player: Player) -> dict:
        """Pobierz statystyki gracza."""
        games = self.session.query(Game).filter_by(player=player).all()
        return {
            'total_games': len(games),
            'total_score': sum(game.score for game in games),
            'avg_score': sum(game.score for game in games) / len(games) if games else 0,
            'max_score': max((game.score for game in games), default=0),
            'total_moves': sum(game.moves_count for game in games),
            'total_time': sum(game.duration for game in games if game.duration),
            'favorite_mode': max(
                (game.game_mode for game in games),
                key=lambda mode: len([g for g in games if g.game_mode == mode])
            ) if games else None
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[dict]:
        """Pobierz tablicę wyników."""
        return [
            {
                'nickname': game.player.nickname,
                'score': game.score,
                'mode': game.game_mode,
                'date': game.completed
            }
            for game in self.session.query(Game)
                .order_by(Game.score.desc())
                .limit(limit)
                .all()
        ] 