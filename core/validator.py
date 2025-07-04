import re
from typing import Optional, Dict, Any
from datetime import datetime

class Validator:
    """Klasa do walidacji danych wejściowych z użyciem wyrażeń regularnych."""
    
    # Wzorce regex dla różnych typów danych
    PATTERNS = {
        'nickname': r'^[a-zA-Z0-9_-]{3,20}$',
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'filename': r'^[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+$',
        'game_mode': r'^(classic|ai|time|obstacles|challenge|multiplayer)$',
        'move': r'^(up|down|left|right)$',
        'score': r'^\d+$',
        'board_size': r'^[3-8]$',
        'timestamp': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$'
    }
    
    @staticmethod
    def validate_nickname(nickname: str) -> tuple[bool, str]:
        """Sprawdź poprawność nicku gracza."""
        if not re.match(Validator.PATTERNS['nickname'], nickname):
            return False, "Nick musi mieć 3-20 znaków i może zawierać tylko litery, cyfry, _ i -"
        return True, ""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Sprawdź poprawność adresu email."""
        if not re.match(Validator.PATTERNS['email'], email):
            return False, "Nieprawidłowy format adresu email"
        return True, ""
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, str]:
        """Sprawdź poprawność nazwy pliku."""
        if not re.match(Validator.PATTERNS['filename'], filename):
            return False, "Nazwa pliku może zawierać tylko litery, cyfry, _ i - oraz musi mieć rozszerzenie"
        return True, ""
    
    @staticmethod
    def validate_game_mode(mode: str) -> tuple[bool, str]:
        """Sprawdź poprawność trybu gry."""
        if not re.match(Validator.PATTERNS['game_mode'], mode.lower()):
            return False, "Nieprawidłowy tryb gry"
        return True, ""
    
    @staticmethod
    def validate_move(move: str) -> tuple[bool, str]:
        """Sprawdź poprawność ruchu."""
        if not re.match(Validator.PATTERNS['move'], move.lower()):
            return False, "Nieprawidłowy ruch"
        return True, ""
    
    @staticmethod
    def validate_score(score: str) -> tuple[bool, str]:
        """Sprawdź poprawność wyniku."""
        if not re.match(Validator.PATTERNS['score'], str(score)):
            return False, "Wynik musi być liczbą całkowitą nieujemną"
        return True, ""
    
    @staticmethod
    def validate_board_size(size: str) -> tuple[bool, str]:
        """Sprawdź poprawność rozmiaru planszy."""
        if not re.match(Validator.PATTERNS['board_size'], str(size)):
            return False, "Rozmiar planszy musi być liczbą od 3 do 8"
        return True, ""
    
    @staticmethod
    def validate_timestamp(timestamp: str) -> tuple[bool, str]:
        """Sprawdź poprawność znacznika czasu."""
        if not re.match(Validator.PATTERNS['timestamp'], timestamp):
            return False, "Nieprawidłowy format znacznika czasu"
        return True, ""
    
    @staticmethod
    def validate_save_data(data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Walidacja danych zapisu gry."""
        errors = []
        
        # Sprawdź wymagane pola
        required_fields = ['board', 'score', 'player_nickname', 'timestamp']
        for field in required_fields:
            if field not in data:
                errors.append(f"Brak wymaganego pola: {field}")
        
        if errors:
            return False, errors
        
        # Walidacja poszczególnych pól
        if not isinstance(data['board'], list):
            errors.append("Plansza musi być listą")
        else:
            # Sprawdź wymiary i zawartość planszy
            size = len(data['board'])
            if not (3 <= size <= 8):
                errors.append("Nieprawidłowy rozmiar planszy")
            else:
                for row in data['board']:
                    if not isinstance(row, list) or len(row) != size:
                        errors.append("Nieprawidłowy format wiersza planszy")
                        break
                    for cell in row:
                        if not isinstance(cell, (int, str)):
                            errors.append("Nieprawidłowa wartość w komórce planszy")
                            break
        
        # Walidacja wyniku
        valid, msg = Validator.validate_score(str(data['score']))
        if not valid:
            errors.append(msg)
        
        # Walidacja nicku gracza
        valid, msg = Validator.validate_nickname(data['player_nickname'])
        if not valid:
            errors.append(msg)
        
        # Walidacja znacznika czasu
        valid, msg = Validator.validate_timestamp(data['timestamp'])
        if not valid:
            errors.append(msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def extract_log_info(log_line: str) -> Optional[Dict[str, str]]:
        """Wyciągnij informacje z linii logu za pomocą regex."""
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (.+)$'
        match = re.match(pattern, log_line)
        
        if match:
            return {
                'timestamp': match.group(1),
                'level': match.group(2),
                'message': match.group(3)
            }
        return None
    
    @staticmethod
    def parse_config_file(content: str) -> Dict[str, Any]:
        """Parsuj plik konfiguracyjny za pomocą regex."""
        config = {}
        
        # Wzorzec dla linii konfiguracyjnej: klucz = wartość
        pattern = r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?)\s*$'
        
        for line in content.split('\n'):
            # Pomiń komentarze i puste linie
            if line.strip() and not line.strip().startswith('#'):
                match = re.match(pattern, line)
                if match:
                    key, value = match.groups()
                    # Próba konwersji wartości na odpowiedni typ
                    try:
                        # Dla wartości liczbowych
                        if re.match(r'^\d+$', value):
                            config[key] = int(value)
                        # Dla wartości zmiennoprzecinkowych
                        elif re.match(r'^\d*\.\d+$', value):
                            config[key] = float(value)
                        # Dla wartości logicznych
                        elif value.lower() in ('true', 'false'):
                            config[key] = value.lower() == 'true'
                        # Dla list (wartości oddzielone przecinkami)
                        elif ',' in value:
                            config[key] = [v.strip() for v in value.split(',')]
                        # Dla zwykłych stringów
                        else:
                            config[key] = value
                    except ValueError:
                        config[key] = value
        
        return config 