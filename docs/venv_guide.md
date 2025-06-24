# Przewodnik po środowiskach wirtualnych (venv) w Pythonie

## Co to jest środowisko wirtualne?

Środowisko wirtualne (venv) to izolowana przestrzeń w systemie, gdzie możemy instalować pakiety Pythona bez wpływania na inne projekty czy systemową instalację Pythona. To jak stworzenie osobnego "pudełka" dla każdego projektu.

### Zalety używania venv:

1. **Izolacja projektów**
   - Każdy projekt ma własne, niezależne zależności
   - Można używać różnych wersji tych samych bibliotek w różnych projektach
   - Unikamy konfliktów między wymaganiami różnych projektów

2. **Czystość systemu**
   - Nie zaśmiecamy systemowej instalacji Pythona
   - Łatwo usunąć środowisko jeśli coś pójdzie nie tak
   - Możemy eksperymentować bez ryzyka uszkodzenia systemu

3. **Reprodukowalność**
   - Łatwo odtworzyć dokładne środowisko na innym komputerze
   - Możemy zamrozić wersje wszystkich zależności
   - Ułatwia pracę zespołową i wdrażanie

## Jak to działa?

1. **Struktura venv**
   ```
   venv/
   ├── Scripts/          # (Windows) lub bin/ (Linux/macOS)
   │   ├── python.exe    # Kopia interpretera Pythona
   │   ├── pip.exe      # Instalator pakietów
   │   └── activate     # Skrypt aktywacyjny
   ├── Lib/
   │   └── site-packages/  # Miejsce na instalowane pakiety
   └── pyvenv.cfg        # Konfiguracja środowiska
   ```

2. **Proces aktywacji**
   - Modyfikuje zmienne środowiskowe
   - Zmienia ścieżkę do interpretera Pythona
   - Zmienia prompt w terminalu (pokazuje nazwę środowiska)

## Podstawowe operacje

### 1. Tworzenie środowiska

```bash
# Windows
python -m venv venv

# Linux/macOS
python3 -m venv venv
```

### 2. Aktywacja środowiska

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

### 3. Sprawdzenie aktywacji

```bash
# Sprawdź ścieżkę do Pythona
where python  # Windows
which python  # Linux/macOS

# Sprawdź zainstalowane pakiety
pip list
```

### 4. Instalacja pakietów

```bash
# Instalacja pojedynczego pakietu
pip install requests

# Instalacja z pliku requirements.txt
pip install -r requirements.txt

# Zapisanie zainstalowanych pakietów
pip freeze > requirements.txt
```

### 5. Deaktywacja środowiska

```bash
deactivate
```

## Dobre praktyki

1. **Nazewnictwo**
   - Używaj nazwy `venv` lub `.venv` dla katalogu środowiska
   - Dodaj katalog środowiska do `.gitignore`

2. **Requirements**
   - Zawsze utrzymuj aktualny plik `requirements.txt`
   - Określaj konkretne wersje pakietów
   - Rozdziel zależności deweloperskie od produkcyjnych

3. **Aktywacja**
   - Zawsze pracuj w aktywowanym środowisku
   - Sprawdzaj czy środowisko jest aktywne przed instalacją pakietów
   - Używaj odpowiedniego skryptu aktywacyjnego dla swojego systemu

4. **Bezpieczeństwo**
   - Regularnie aktualizuj pakiety
   - Sprawdzaj znane podatności w zależnościach
   - Nie przechowuj wrażliwych danych w środowisku

## Rozwiązywanie problemów

### 1. Problemy z uprawnieniami
```bash
# Windows (jako administrator)
python -m venv venv --system-site-packages

# Linux/macOS
sudo python3 -m venv venv
```

### 2. Problemy z aktywacją
```bash
# Windows PowerShell (jeśli występuje błąd wykonywania skryptów)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux/macOS (jeśli source nie działa)
chmod +x venv/bin/activate
```

### 3. Problemy z pakietami
```bash
# Wyczyść cache pip
pip cache purge

# Wymuś reinstalację pakietów
pip install --force-reinstall -r requirements.txt
```

## Alternatywy dla venv

1. **virtualenv**
   - Starszy, ale bardziej rozbudowany
   - Działa ze starszymi wersjami Pythona
   - Więcej opcji konfiguracji

2. **conda**
   - Zarządza nie tylko pakietami Pythona
   - Dobry do projektów naukowych
   - Ma własny system pakietów

3. **pipenv**
   - Łączy funkcje pip i virtualenv
   - Automatycznie zarządza środowiskiem
   - Lepsze zarządzanie zależnościami

4. **poetry**
   - Nowoczesne narzędzie do zarządzania projektami
   - Lepsze rozwiązywanie zależności
   - Wbudowane narzędzia do publikacji pakietów

## Kiedy używać venv?

1. **Zawsze gdy:**
   - Rozpoczynasz nowy projekt
   - Pracujesz nad istniejącym projektem
   - Testujesz nowe biblioteki
   - Chcesz odizolować zależności

2. **Szczególnie ważne gdy:**
   - Projekt ma wiele zależności
   - Pracujesz w zespole
   - Planujesz wdrożenie projektu
   - Eksperymentujesz z nowymi pakietami 