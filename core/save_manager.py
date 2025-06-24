import json
import os
import hashlib
import base64
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import shutil
from .error_handler import ErrorHandler, SaveError

class SaveManager:
    """Klasa zarządzająca zapisami gry."""
    
    def __init__(self, save_dir: str = "saves"):
        """
        Inicjalizacja menedżera zapisów.
        
        Args:
            save_dir (str): Katalog z zapisami gry
        """
        self.save_dir = save_dir
        self.CHECKPOINT_DIR = os.path.join(save_dir, "checkpoints")
        self.AUTOSAVE_DIR = os.path.join(save_dir, "autosave")
        self.QUICKSAVE_DIR = os.path.join(save_dir, "quicksave")
        self.error_handler = ErrorHandler()
        self._ensure_save_dir()
    
    def _ensure_save_dir(self) -> None:
        """Tworzy katalogi na zapisy jeśli nie istnieją."""
        # Utwórz główny katalog zapisów
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Utwórz podkatalogi
        os.makedirs(self.AUTOSAVE_DIR, exist_ok=True)
        os.makedirs(self.QUICKSAVE_DIR, exist_ok=True)
        os.makedirs(self.CHECKPOINT_DIR, exist_ok=True)
        
        # Utwórz plik .gitkeep w każdym katalogu, aby git zachował puste katalogi
        for directory in [self.save_dir, self.AUTOSAVE_DIR, self.QUICKSAVE_DIR, self.CHECKPOINT_DIR]:
            gitkeep_file = os.path.join(directory, '.gitkeep')
            if not os.path.exists(gitkeep_file):
                with open(gitkeep_file, 'w') as f:
                    pass
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of game data for validation.
        
        Args:
            data (Dict[str, Any]): Game data to hash
        
        Returns:
            str: Hash of the data
        """
        # Convert data to stable string representation
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _validate_save(self, data: Dict[str, Any], stored_hash: str) -> bool:
        """Validate save data against stored hash.
        
        Args:
            data (Dict[str, Any]): Game data to validate
            stored_hash (str): Hash to validate against
        
        Returns:
            bool: True if data is valid
        """
        return self._calculate_hash(data) == stored_hash
    
    def save_game(self, game_state: Dict[str, Any], save_name: str) -> bool:
        """
        Zapisuje stan gry.
        
        Args:
            game_state (Dict[str, Any]): Stan gry do zapisania
            save_name (str): Nazwa zapisu
            
        Returns:
            bool: Czy zapis się powiódł
        """
        try:
            # Walidacja danych
            self.error_handler.validate_board(game_state['board'])
            self.error_handler.validate_score(game_state['score'])
            
            # Dodaj metadane
            save_data = {
                'game_data': game_state,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            # Oblicz sumę kontrolną
            save_data['checksum'] = self.error_handler.calculate_checksum(save_data['game_data'])
            
            # Ścieżka do pliku
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            
            # Utwórz kopię zapasową
            self.error_handler.create_backup(save_data, filepath)
            
            # Zapisz plik
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas zapisywania gry '{save_name}'")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        """
        Wczytuje stan gry.
        
        Args:
            save_name (str): Nazwa zapisu
            
        Returns:
            Optional[Dict[str, Any]]: Wczytany stan gry lub None w przypadku błędu
        """
        try:
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            
            if not os.path.exists(filepath):
                raise SaveError(f"Plik zapisu '{save_name}' nie istnieje")
            
            # Sprawdź integralność pliku
            if not self.error_handler.verify_save_file(filepath):
                # Próba przywrócenia z kopii zapasowej
                backup_data = self.error_handler.restore_from_backup(filepath)
                if backup_data is None:
                    raise SaveError("Nie można wczytać gry - plik jest uszkodzony")
                return backup_data['game_data']
            
            # Wczytaj plik
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return data['game_data']
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas wczytywania gry '{save_name}'")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        Zwraca listę dostępnych zapisów.
        
        Returns:
            List[Dict[str, Any]]: Lista zapisów z metadanymi
        """
        saves = []
        
        try:
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        
                        if self.error_handler.verify_save_file(filepath):
                            saves.append({
                                'name': filename[:-5],  # Usuń .json
                                'timestamp': data['metadata']['timestamp'],
                                'score': data['game_data']['score']
                            })
                    except:
                        continue
            
            return sorted(saves, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas listowania zapisów")
            return []
    
    def delete_save(self, save_name: str) -> bool:
        """
        Usuwa zapis gry.
        
        Args:
            save_name (str): Nazwa zapisu
            
        Returns:
            bool: Czy usunięcie się powiodło
        """
        try:
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas usuwania zapisu '{save_name}'")
            return False
    
    def create_autosave(self, game_state: Dict[str, Any]) -> bool:
        """
        Tworzy automatyczny zapis gry.
        
        Args:
            game_state (Dict[str, Any]): Stan gry do zapisania
            
        Returns:
            bool: Czy autozapis się powiódł
        """
        autosave_dir = os.path.join(self.save_dir, "autosave")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.save_game(game_state, f"autosave/{timestamp}")
    
    def create_quicksave(self, game_state: Dict[str, Any], slot: int = 1) -> bool:
        """
        Tworzy szybki zapis gry.
        
        Args:
            game_state (Dict[str, Any]): Stan gry do zapisania
            slot (int): Numer slotu (1-5)
            
        Returns:
            bool: Czy szybki zapis się powiódł
        """
        if not 1 <= slot <= 5:
            raise ValueError("Numer slotu musi być z zakresu 1-5")
        
        return self.save_game(game_state, f"quicksave/slot_{slot}")
    
    def cleanup_old_saves(self, max_autosaves: int = 10) -> None:
        """
        Czyści stare automatyczne zapisy.
        
        Args:
            max_autosaves (int): Maksymalna liczba autozapisów do zachowania
        """
        try:
            autosave_dir = os.path.join(self.save_dir, "autosave")
            autosaves = sorted([
                f for f in os.listdir(autosave_dir)
                if f.endswith('.json')
            ])
            
            # Usuń najstarsze zapisy, zachowując max_autosaves najnowszych
            if len(autosaves) > max_autosaves:
                for old_save in autosaves[:-max_autosaves]:
                    os.remove(os.path.join(autosave_dir, old_save))
                    
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas czyszczenia starych zapisów")
    
    def create_checkpoint(self, game_state: Dict[str, Any], name: Optional[str] = None) -> str:
        """Tworzy checkpoint gry.
        
        Args:
            game_state (Dict[str, Any]): Stan gry do zapisania
            name (Optional[str]): Opcjonalna nazwa checkpointu
            
        Returns:
            str: Nazwa utworzonego pliku checkpointu
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_name = name if name else f"checkpoint_{timestamp}"
            checkpoint_file = os.path.join(self.CHECKPOINT_DIR, f"{checkpoint_name}.json")
            
            # Dodaj metadane
            save_data = {
                'game_data': game_state,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'name': checkpoint_name,
                    'type': 'checkpoint'
                }
            }
            
            # Oblicz sumę kontrolną
            save_data['checksum'] = self.error_handler.calculate_checksum(save_data['game_data'])
            
            # Zapisz plik
            with open(checkpoint_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return checkpoint_name
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas tworzenia checkpointu")
            return ""
    
    def load_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """Wczytuje checkpoint gry.
        
        Args:
            checkpoint_name (str): Nazwa checkpointu do wczytania
            
        Returns:
            Optional[Dict[str, Any]]: Wczytany stan gry lub None w przypadku błędu
        """
        try:
            checkpoint_file = os.path.join(self.CHECKPOINT_DIR, f"{checkpoint_name}.json")
            
            if not os.path.exists(checkpoint_file):
                raise SaveError(f"Checkpoint '{checkpoint_name}' nie istnieje")
            
            # Wczytaj plik
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            
            # Sprawdź sumę kontrolną
            if not self._validate_save(data['game_data'], data['checksum']):
                raise SaveError("Checkpoint jest uszkodzony")
            
            return data['game_data']
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas wczytywania checkpointu '{checkpoint_name}'")
            return None
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Zwraca listę dostępnych checkpointów.
        
        Returns:
            List[Dict[str, Any]]: Lista checkpointów z metadanymi
        """
        checkpoints = []
        
        try:
            if not os.path.exists(self.CHECKPOINT_DIR):
                return []
                
            for filename in os.listdir(self.CHECKPOINT_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.CHECKPOINT_DIR, filename)
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        
                        if self._validate_save(data['game_data'], data['checksum']):
                            checkpoints.append({
                                'name': data['metadata']['name'],
                                'timestamp': data['metadata']['timestamp'],
                                'score': data['game_data']['score']
                            })
                    except:
                        continue
            
            return sorted(checkpoints, key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas listowania checkpointów")
            return []
    
    def export_game(self, game_data: Dict[str, Any], filepath: str) -> bool:
        """Export game state to a file that can be imported later.
        
        Args:
            game_data (Dict[str, Any]): Game state to export
            filepath (str): Path to save the export file
        
        Returns:
            bool: True if export was successful
        """
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "game_data": game_data
            }
            
            # Calculate hash
            data_hash = self._calculate_hash(export_data)
            
            # Combine data and hash
            final_data = {
                "data": export_data,
                "hash": data_hash
            }
            
            # Convert to base64 for easier sharing
            encoded_data = base64.b64encode(
                json.dumps(final_data).encode()
            ).decode()
            
            with open(filepath, 'w') as f:
                f.write(encoded_data)
            
            return True
            
        except Exception as e:
            print(f"Error exporting game: {e}")
            return False
    
    def import_game(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Import game state from an exported file.
        
        Args:
            filepath (str): Path to the export file (with or without extension)
            
        Returns:
            Optional[Dict[str, Any]]: Imported game state or None if invalid
        """
        try:
            # Sprawdź różne warianty nazwy pliku
            possible_paths = [
                filepath,
                f"{filepath}.2048",
                os.path.join(self.save_dir, filepath),
                os.path.join(self.save_dir, f"{filepath}.2048")
            ]
            
            # Znajdź pierwszy istniejący plik
            existing_path = next((path for path in possible_paths if os.path.exists(path)), None)
            
            if not existing_path:
                print("Nie znaleziono pliku do importu!")
                return None
            
            # Wczytaj i zdekoduj dane
            with open(existing_path, 'r') as f:
                encoded_data = f.read()
            
            # Dekoduj base64
            decoded_data = base64.b64decode(encoded_data).decode()
            import_data = json.loads(decoded_data)
            
            # Walidacja danych
            if not self._validate_save(import_data["data"], import_data["hash"]):
                print("Uwaga: Plik importu wydaje się być uszkodzony!")
                return None
            
            return import_data["data"]["game_data"]
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas importu gry")
            return None 