from typing import Any, Optional, Dict
import json
import hashlib
import logging
from datetime import datetime
import os
from colorama import Fore, Style

class GameError(Exception):
    pass

class ValidationError(GameError):
    pass

class SaveError(GameError):
    pass

class ErrorHandler:
    
    def __init__(self, log_file: str = "game_errors.log"):
        self.log_file = log_file
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    @staticmethod
    def validate_board(board: list) -> bool:
        if not isinstance(board, list):
            raise ValidationError("Plansza musi być listą")
        
        size = len(board)
        if size < 4:
            raise ValidationError("Plansza jest za mała")
        
        for row in board:
            if not isinstance(row, list) or len(row) != size:
                raise ValidationError("Nieprawidłowy rozmiar wiersza")
            for cell in row:
                if not isinstance(cell, (int, str)):
                    raise ValidationError("Nieprawidłowa wartość w komórce")
                if isinstance(cell, int) and (cell < 0 or (cell & (cell - 1) != 0 and cell != 0)):
                    raise ValidationError("Nieprawidłowa wartość liczby (musi być potęgą 2)")
        
        return True
    
    @staticmethod
    def validate_score(score: int) -> bool:
        if not isinstance(score, int):
            raise ValidationError("Wynik musi być liczbą całkowitą")
        if score < 0:
            raise ValidationError("Wynik nie może być ujemny")
        return True
    
    @staticmethod
    def calculate_checksum(data: Dict[str, Any]) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_save_file(self, filepath: str) -> bool:
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if 'checksum' not in data or 'game_data' not in data:
                return False
            
            stored_checksum = data['checksum']
            calculated_checksum = self.calculate_checksum(data['game_data'])
            
            return stored_checksum == calculated_checksum
        except Exception as e:
            logging.error(f"Błąd weryfikacji pliku zapisu: {str(e)}")
            return False
    
    def create_backup(self, data: Dict[str, Any], filepath: str) -> None:
        
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
        
        try:
            with open(backup_path, 'w') as f:
                json.dump(data, f)
            logging.info(f"Utworzono kopię zapasową: {backup_path}")
        except Exception as e:
            logging.error(f"Błąd tworzenia kopii zapasowej: {str(e)}")
    
    def restore_from_backup(self, filepath: str) -> Optional[Dict[str, Any]]:
        
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            return None
        
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_")],
                        reverse=True)
        
        for backup in backups:
            backup_path = os.path.join(backup_dir, backup)
            try:
                with open(backup_path, 'r') as f:
                    data = json.load(f)
                if self.verify_save_file(backup_path):
                    logging.info(f"Przywrócono dane z kopii: {backup_path}")
                    return data
            except Exception as e:
                logging.error(f"Błąd odczytu kopii zapasowej {backup_path}: {str(e)}")
        
        return None
    
    @staticmethod
    def display_error(message: str, error_type: str = "ERROR") -> None:
        
        print(f"\n{Fore.RED}[{error_type}] {message}{Style.RESET_ALL}")
        print("Naciśnij dowolny klawisz, aby kontynuować...")
        input()
    
    def log_error(self, error: Exception, context: str = "") -> None:
        
        error_msg = f"{context}: {str(error)}" if context else str(error)
        logging.error(error_msg)
        self.display_error(error_msg) 