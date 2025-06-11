from typing import List, Dict, Any, Callable
from functools import reduce
from itertools import chain
import operator

class FunctionalGameUtils:
    
    @staticmethod
    def calculate_board_stats(board: List[List[int]]) -> Dict[str, int]:
        flat_board = list(chain.from_iterable(board))
        
        non_empty = list(filter(lambda x: x != 0, flat_board))
        
        tile_levels = list(map(lambda x: x.bit_length() - 1 if x > 0 else 0, non_empty))
        
        return {
            'max_tile': max(flat_board, default=0),
            'non_empty_count': len(non_empty),
            'sum_values': sum(non_empty),
            'avg_level': sum(tile_levels) / len(tile_levels) if tile_levels else 0
        }
    
    @staticmethod
    def analyze_moves_history(moves: List[Dict[str, Any]]) -> Dict[str, Any]:
        directions = list(map(lambda x: x['direction'], moves))
        
        direction_counts = reduce(
            lambda acc, curr: {**acc, curr: acc.get(curr, 0) + 1},
            directions,
            {}
        )
        
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
        game_durations = (
            game['duration']
            for game in games
            if 'duration' in game and game['duration'] is not None
        )
        
        scores = [game['score'] for game in games if 'score' in game]
        
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
        calculate_rank_score = lambda p: (
            p.get('max_score', 0) * 0.5 +
            p.get('games_won', 0) * 100 +
            p.get('total_games', 0) * 10
        )
        
        ranked_players = map(
            lambda p: {**p, 'rank_score': calculate_rank_score(p)},
            players
        )
        
        sorted_players = sorted(
            ranked_players,
            key=lambda p: p['rank_score'],
            reverse=True
        )
        
        return list(map(
            lambda x: {**x[1], 'rank': x[0] + 1},
            enumerate(sorted_players)
        ))
    
    @staticmethod
    def analyze_game_patterns(moves: List[str]) -> Dict[str, Any]:
        move_pairs = list(zip(moves[:-1], moves[1:]))
        
        pattern_counts = reduce(
            lambda acc, pair: {**acc, pair: acc.get(pair, 0) + 1},
            move_pairs,
            {}
        )
        
        common_patterns = sorted(
            pattern_counts.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:3]
        
        move_diversity = len(set(moves)) / 4
        
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
        calc_duration = lambda start, end: (end - start).total_seconds() / 60
        
        scoring_moves = (
            move for move in game_data.get('moves', [])
            if move.get('score_change', 0) > 0
        )
        
        effective_moves = [
            move for move in game_data.get('moves', [])
            if move.get('score_change', 0) >= 4
        ]
            
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