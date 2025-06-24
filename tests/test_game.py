import pytest
from unittest.mock import Mock, patch
from core.board import Board
from core.game import Game
from core.player import Player
from core.validator import Validator
from core.database import DatabaseManager
import os

@pytest.fixture
def board():
    """Fixture dostarczająca czystą planszę do testów."""
    return Board(4)

@pytest.fixture
def player():
    """Fixture dostarczająca obiekt gracza do testów."""
    return Player("TestPlayer")

@pytest.fixture
def game(player):
    """Fixture dostarczająca obiekt gry do testów."""
    return Game(player=player)

@pytest.fixture
def db():
    """Fixture dostarczająca testową bazę danych."""
    db_path = "test_game_data.db"
    db = DatabaseManager(db_path)
    yield db
    # Cleanup po testach
    if os.path.exists(db_path):
        os.remove(db_path)

def test_board_initialization(board):
    """Test inicjalizacji planszy."""
    assert len(board.board) == 4
    assert len(board.board[0]) == 4
    # Sprawdź czy są dokładnie dwie początkowe płytki
    non_zero_tiles = sum(1 for row in board.board for cell in row if cell != 0)
    assert non_zero_tiles == 2

def test_board_move(board):
    """Test ruchu na planszy."""
    # Ustaw znaną konfigurację planszy
    board.board = [
        [2, 0, 0, 0],
        [2, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    # Wykonaj ruch w górę
    board.move('up')
    # Sprawdź czy płytki się połączyły
    assert board.board[0][0] == 4
    assert board.board[1][0] == 0

def test_game_over_detection(board):
    """Test wykrywania końca gry."""
    # Wypełnij planszę bez możliwości ruchu
    board.board = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 2]
    ]
    assert board.is_game_over() == True

def test_win_detection(board):
    """Test wykrywania wygranej."""
    # Ustaw płytkę 2048
    board.board[0][0] = 2048
    assert board.has_won() == True

@pytest.mark.parametrize("nickname,expected", [
    ("valid_nick", True),
    ("ab", False),  # Za krótki
    ("very_very_very_long_nick", False),  # Za długi
    ("invalid@nick", False),  # Niedozwolone znaki
])
def test_nickname_validation(nickname, expected):
    """Test walidacji nicków graczy."""
    valid, _ = Validator.validate_nickname(nickname)
    assert valid == expected

def test_save_and_load_game(game, tmp_path):
    """Test zapisywania i wczytywania stanu gry."""
    # Przygotuj stan gry
    game.board.board[0][0] = 2
    game.board.score = 100
    
    # Zapisz grę
    save_path = tmp_path / "test_save.json"
    assert game.save_game(str(save_path)) == True
    
    # Stwórz nową grę i wczytaj zapisany stan
    new_game = Game()
    assert new_game.load_game(str(save_path)) == True
    
    # Sprawdź czy stan został prawidłowo wczytany
    assert new_game.board.board[0][0] == 2
    assert new_game.board.score == 100

@pytest.mark.parametrize("direction,expected_score", [
    ('up', 4),
    ('down', 4),
    ('left', 4),
    ('right', 4),
])
def test_move_scoring(board, direction, expected_score):
    """Test punktacji po ruchu."""
    # Ustaw planszę z dwoma płytkami 2 obok siebie
    board.board = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.move(direction)
    assert board.score == expected_score

def test_database_operations(db, player):
    """Test operacji na bazie danych."""
    # Dodaj gracza
    db_player = db.add_player(player.nickname)
    assert db_player.nickname == player.nickname
    
    # Rozpocznij grę
    game = db.start_game(db_player, "classic")
    assert game.player_id == db_player.id
    assert game.game_mode == "classic"
    
    # Dodaj ruch
    db.add_move(game, "up", 4)
    assert game.moves_count == 1
    
    # Zakończ grę
    db.update_game(game, 100, 8)
    db.complete_game(game)
    assert game.score == 100
    assert game.max_tile == 8
    assert game.completed is not None

@patch('core.board.Board._add_new_tile')
def test_move_mechanics(mock_add_tile, board):
    """Test mechaniki ruchu z mockowaniem dodawania nowych płytek."""
    board.board = [
        [2, 0, 2, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    
    # Wykonaj ruch w lewo
    board.move('left')
    
    # Sprawdź czy płytki zostały prawidłowo połączone
    assert board.board[0][0] == 4
    assert board.board[0][1] == 0
    assert board.board[0][2] == 0
    assert board.board[0][3] == 0
    
    # Sprawdź czy metoda dodawania nowej płytki została wywołana
    mock_add_tile.assert_called_once()

def test_undo_functionality(game):
    """Test funkcjonalności cofania ruchu."""
    # Zapisz początkowy stan
    initial_board = [row[:] for row in game.board.board]
    initial_score = game.board.score
    
    # Wykonaj ruch
    game.board.move('right')
    
    # Cofnij ruch
    assert game.board.undo() == True
    
    # Sprawdź czy stan wrócił do początkowego
    assert game.board.score == initial_score
    for i in range(4):
        for j in range(4):
            assert game.board.board[i][j] == initial_board[i][j]

def test_game_statistics(game, db):
    """Test zbierania statystyk gry."""
    # Dodaj gracza do bazy
    db_player = db.add_player(game.player.nickname)
    game_session = db.start_game(db_player, "classic")
    
    # Symuluj kilka ruchów
    moves = ['up', 'right', 'down', 'left']
    for move in moves:
        game.board.move(move)
        db.add_move(game_session, move, game.board.score)
    
    # Zakończ grę
    db.update_game(game_session, game.board.score, 8)
    db.complete_game(game_session)
    
    # Pobierz statystyki
    stats = db.get_player_stats(db_player)
    
    # Sprawdź statystyki
    assert stats['total_games'] == 1
    assert stats['total_moves'] == len(moves)
    assert stats['favorite_mode'] == "classic" 