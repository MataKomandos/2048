from typing import List, Dict, Any, Callable
from functools import reduce
from itertools import chain
import operator

class FunctionalGameUtils:
    """Klasa z funkcjami wyższego rzędu do przetwarzania danych gry."""
    
    @staticmethod
    def calculate_board_stats(board: List[List[int]]) -> Dict[str, int]:
        """Oblicz statystyki planszy używając funkcji wyższego rzędu."""
        # Spłaszcz planszę do jednej listy używając chain
        flat_board = list(chain.from_iterable(board))
        
        # Użyj filter do znalezienia niepustych pól
        non_empty = list(filter(lambda x: x != 0, flat_board))
        
        # Użyj map do obliczenia logarytmów
        tile_levels = list(map(lambda x: x.bit_length() - 1 if x > 0 else 0, non_empty))
        
        return {
            'max_tile': max(flat_board, default=0),
            'non_empty_count': len(non_empty),
            'sum_values': sum(non_empty),
            'avg_level': sum(tile_levels) / len(tile_levels) if tile_levels else 0
        }
    
    @staticmethod
    def analyze_moves_history(moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analizuj historię ruchów używając funkcji wyższego rzędu."""
        # Użyj map do wyodrębnienia kierunków
        directions = list(map(lambda x: x['direction'], moves))
        
        # Użyj reduce do zliczenia wystąpień każdego kierunku
        direction_counts = reduce(
            lambda acc, curr: {**acc, curr: acc.get(curr, 0) + 1},
            directions,
            {}
        )
        
        # Użyj map i reduce do obliczenia średniej zmiany wyniku
        score_changes = list(map(lambda x: x.get('score_change', 0), moves))
        avg_score_change = reduce(operator.add, score_changes, 0) / len(moves) if moves else 0
        
        return {
            'direction_counts': direction_counts,
            'most_common_direction': max(direction_counts.items(), key=operator.itemgetter(1))[0] if direction_counts else None,
            'avg_score_change': avg_score_change,
            'total_moves': len(moves)
        }
    
    @staticmethod
    def process_game_history(games: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Przetwórz historię gier używając funkcji wyższego rzędu."""
        # Generator dla czasów gier
        game_durations = (
            game['duration']
            for game in games
            if 'duration' in game and game['duration'] is not None
        )
        
        # List comprehension dla wyników
        scores = [game['score'] for game in games if 'score' in game]
        
        # Dictionary comprehension dla trybów gry
        mode_games = {
            mode: len([g for g in games if g.get('game_mode') == mode])
            for mode in set(g.get('game_mode') for g in games if 'game_mode' in g)
        }
        
        return {
            'total_games': len(games),
            'avg_duration': sum(game_durations) / len(games) if games else 0,
            'max_score': max(scores, default=0),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'mode_distribution': mode_games
        }
    
    @staticmethod
    def calculate_player_ranking(players: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Oblicz ranking graczy używając funkcji wyższego rzędu."""
        # Funkcja do obliczania wyniku rankingowego
        calculate_rank_score = lambda p: (
            p.get('max_score', 0) * 0.5 +
            p.get('games_won', 0) * 100 +
            p.get('total_games', 0) * 10
        )
        
        # Użyj map do obliczenia wyników rankingowych
        ranked_players = map(
            lambda p: {**p, 'rank_score': calculate_rank_score(p)},
            players
        )
        
        # Posortuj graczy po wyniku rankingowym
        sorted_players = sorted(
            ranked_players,
            key=lambda p: p['rank_score'],
            reverse=True
        )
        
        # Użyj enumerate i map do dodania pozycji w rankingu
        return list(map(
            lambda x: {**x[1], 'rank': x[0] + 1},
            enumerate(sorted_players)
        ))
    
    @staticmethod
    def analyze_game_patterns(moves: List[str]) -> Dict[str, Any]:
        """Analizuj wzorce w ruchach gracza używając funkcji wyższego rzędu."""
        # Utwórz pary kolejnych ruchów
        move_pairs = list(zip(moves[:-1], moves[1:]))
        
        # Użyj reduce do zliczenia sekwencji ruchów
        pattern_counts = reduce(
            lambda acc, pair: {**acc, pair: acc.get(pair, 0) + 1},
            move_pairs,
            {}
        )
        
        # Znajdź najczęstsze wzorce
        common_patterns = sorted(
            pattern_counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:3]
        
        # Oblicz różnorodność ruchów
        move_diversity = len(set(moves)) / 4  # 4 to maksymalna liczba różnych ruchów
        
        # Użyj map do analizy zmian kierunku
        direction_changes = list(map(
            lambda x: x[0] != x[1],
            move_pairs
        ))
        
        return {
            'common_patterns': common_patterns,
            'move_diversity': move_diversity,
            'direction_changes_ratio': sum(direction_changes) / len(direction_changes) if direction_changes else 0
        }
    
    @staticmethod
    def generate_game_summary(game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generuj podsumowanie gry używając funkcji wyższego rzędu."""
        # Lambda do obliczania czasu gry w minutach
        calc_duration = lambda start, end: (end - start).total_seconds() / 60
        
        # Generator dla ruchów z punktami
        scoring_moves = (
            move for move in game_data.get('moves', [])
            if move.get('score_change', 0) > 0
        )
        
        # List comprehension dla efektywnych ruchów
        effective_moves = [
            move for move in game_data.get('moves', [])
            if move.get('score_change', 0) >= 4
        ]
        
        # Oblicz statystyki używając reduce
        move_stats = reduce(
            lambda acc, move: {
                'total_score': acc['total_score'] + move.get('score_change', 0),
                'max_single_score': max(acc['max_single_score'], move.get('score_change', 0)),
                'moves_count': acc['moves_count'] + 1
            },
            game_data.get('moves', []),
            {'total_score': 0, 'max_single_score': 0, 'moves_count': 0}
        )
        
        return {
            'duration_minutes': calc_duration(game_data['start_time'], game_data['end_time']),
            'scoring_moves_ratio': len(list(scoring_moves)) / len(game_data.get('moves', [])) if game_data.get('moves') else 0,
            'effective_moves_ratio': len(effective_moves) / len(game_data.get('moves', [])) if game_data.get('moves') else 0,
            'avg_score_per_move': move_stats['total_score'] / move_stats['moves_count'] if move_stats['moves_count'] > 0 else 0,
            'max_single_move_score': move_stats['max_single_score']
        } 