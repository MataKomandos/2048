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
    
    def __init__(self, save_dir: str = "saves"):
        
        self.save_dir = save_dir
        self.CHECKPOINT_DIR = os.path.join(save_dir, "checkpoints")
        self.AUTOSAVE_DIR = os.path.join(save_dir, "autosave")
        self.QUICKSAVE_DIR = os.path.join(save_dir, "quicksave")
        self.error_handler = ErrorHandler()
        self._ensure_save_dir()
    
    def _ensure_save_dir(self) -> None:
        
        os.makedirs(self.save_dir, exist_ok=True)
        
        os.makedirs(self.AUTOSAVE_DIR, exist_ok=True)
        os.makedirs(self.QUICKSAVE_DIR, exist_ok=True)
        os.makedirs(self.CHECKPOINT_DIR, exist_ok=True)
        
        for directory in [self.save_dir, self.AUTOSAVE_DIR, self.QUICKSAVE_DIR, self.CHECKPOINT_DIR]:
            gitkeep_file = os.path.join(directory, '.gitkeep')
            if not os.path.exists(gitkeep_file):
                with open(gitkeep_file, 'w') as f:
                    pass
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _validate_save(self, data: Dict[str, Any], stored_hash: str) -> bool:
        
        return self._calculate_hash(data) == stored_hash
    
    def save_game(self, game_state: Dict[str, Any], save_name: str) -> bool:

        try:
            self.error_handler.validate_board(game_state['board'])
            self.error_handler.validate_score(game_state['score'])
            
            save_data = {
                'game_data': game_state,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            save_data['checksum'] = self.error_handler.calculate_checksum(save_data['game_data'])
            
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            
            self.error_handler.create_backup(save_data, filepath)
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas zapisywania gry '{save_name}'")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict[str, Any]]:
        
        try:
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            
            if not os.path.exists(filepath):
                raise SaveError(f"Plik zapisu '{save_name}' nie istnieje")
            
            if not self.error_handler.verify_save_file(filepath):
                backup_data = self.error_handler.restore_from_backup(filepath)
                if backup_data is None:
                    raise SaveError("Nie można wczytać gry - plik jest uszkodzony")
                return backup_data['game_data']
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return data['game_data']
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas wczytywania gry '{save_name}'")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        
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
                                'name': filename[:-5],
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

        try:
            filepath = os.path.join(self.save_dir, f"{save_name}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas usuwania zapisu '{save_name}'")
            return False
    
    def create_autosave(self, game_state: Dict[str, Any]) -> bool:

        autosave_dir = os.path.join(self.save_dir, "autosave")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.save_game(game_state, f"autosave/{timestamp}")
    
    def create_quicksave(self, game_state: Dict[str, Any], slot: int = 1) -> bool:

        if not 1 <= slot <= 5:
            raise ValueError("Numer slotu musi być z zakresu 1-5")
        
        return self.save_game(game_state, f"quicksave/slot_{slot}")
    
    def cleanup_old_saves(self, max_autosaves: int = 10) -> None:

        try:
            autosave_dir = os.path.join(self.save_dir, "autosave")
            autosaves = sorted([
                f for f in os.listdir(autosave_dir)
                if f.endswith('.json')
            ])
            
            if len(autosaves) > max_autosaves:
                for old_save in autosaves[:-max_autosaves]:
                    os.remove(os.path.join(autosave_dir, old_save))
                    
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas czyszczenia starych zapisów")
    
    def create_checkpoint(self, game_state: Dict[str, Any], name: Optional[str] = None) -> str:

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            checkpoint_name = name if name else f"checkpoint_{timestamp}"
            checkpoint_file = os.path.join(self.CHECKPOINT_DIR, f"{checkpoint_name}.json")
            
            save_data = {
                'game_data': game_state,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'name': checkpoint_name,
                    'type': 'checkpoint'
                }
            }
            
            save_data['checksum'] = self.error_handler.calculate_checksum(save_data['game_data'])
            
            with open(checkpoint_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return checkpoint_name
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas tworzenia checkpointu")
            return ""
    
    def load_checkpoint(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:

        try:
            checkpoint_file = os.path.join(self.CHECKPOINT_DIR, f"{checkpoint_name}.json")
            
            if not os.path.exists(checkpoint_file):
                raise SaveError(f"Checkpoint '{checkpoint_name}' nie istnieje")
            
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
            
            if not self._validate_save(data['game_data'], data['checksum']):
                raise SaveError("Checkpoint jest uszkodzony")
            
            return data['game_data']
            
        except Exception as e:
            self.error_handler.log_error(e, f"Błąd podczas wczytywania checkpointu '{checkpoint_name}'")
            return None
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:

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

        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "game_data": game_data
            }
            
            data_hash = self._calculate_hash(export_data)
            
            final_data = {
                "data": export_data,
                "hash": data_hash
            }
            
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

        try:
            possible_paths = [
                filepath,
                f"{filepath}.2048",
                os.path.join(self.save_dir, filepath),
                os.path.join(self.save_dir, f"{filepath}.2048")
            ]

            existing_path = next((path for path in possible_paths if os.path.exists(path)), None)
            
            if not existing_path:
                print("Nie znaleziono pliku do importu!")
                return None
            
            with open(existing_path, 'r') as f:
                encoded_data = f.read()
            
            decoded_data = base64.b64decode(encoded_data).decode()
            import_data = json.loads(decoded_data)
            
            if not self._validate_save(import_data["data"], import_data["hash"]):
                print("Uwaga: Plik importu wydaje się być uszkodzony!")
                return None
            
            return import_data["data"]["game_data"]
            
        except Exception as e:
            self.error_handler.log_error(e, "Błąd podczas importu gry")
            return None 