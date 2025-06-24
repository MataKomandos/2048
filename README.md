# 2048 - Gra Logiczna

## Opis
Implementacja popularnej gry logicznej 2048 w Pythonie z dodatkowymi funkcjami i trybami gry. Gra polega na łączeniu kafelków o tych samych wartościach poprzez przesuwanie ich w czterech kierunkach, aby osiągnąć kafelek o wartości 2048 lub wyższej.

### Funkcje
- Różne tryby gry:
  - Klasyczny
  - Gra z AI
  - Tryb czasowy
  - Tryb z przeszkodami
  - Tryb wyzwań
  - Gra dwuosobowa
- System osiągnięć
- Statystyki i wykresy postępów
- Automatyczne zapisywanie
- System cofania ruchów
- Różne motywy graficzne
- Baza danych z historią gier
- Eksport i import stanu gry

## Wymagania systemowe
- Python 3.8 lub nowszy
- Biblioteki wymienione w `requirements.txt`
- Około 100MB wolnego miejsca na dysku
- Terminal obsługujący kolory ANSI (dla Windows zalecany Windows Terminal)

## Instalacja i konfiguracja środowiska

### 1. Przygotowanie środowiska

Najpierw upewnij się, że masz zainstalowanego Pythona 3.8 lub nowszego:
```bash
python --version
```

Jeśli nie masz Pythona, pobierz go ze strony [python.org](https://www.python.org/downloads/).

### 2. Pobranie projektu

Sklonuj repozytorium:
```bash
git clone [adres-repozytorium]
cd 2048
```

### 3. Utworzenie wirtualnego środowiska

#### Windows
```bash
# Utworzenie środowiska
python -m venv venv

# Aktywacja środowiska
venv\Scripts\activate

# Sprawdzenie czy środowisko jest aktywne
where python
# Powinno pokazać ścieżkę do pythona w katalogu venv
```

#### Linux/macOS
```bash
# Utworzenie środowiska
python3 -m venv venv

# Aktywacja środowiska
source venv/bin/activate

# Sprawdzenie czy środowisko jest aktywne
which python
# Powinno pokazać ścieżkę do pythona w katalogu venv
```

### 4. Instalacja zależności

#### Podstawowa instalacja
```bash
# Aktualizacja pip
python -m pip install --upgrade pip

# Instalacja podstawowych zależności
pip install -r requirements.txt
```

#### Instalacja dla deweloperów
```bash
# Instalacja z dodatkowymi narzędziami deweloperskimi
pip install -e ".[dev]"
```

### 5. Weryfikacja instalacji

```bash
# Sprawdź czy wszystkie zależności są zainstalowane
pip freeze

# Uruchom testy (jeśli zainstalowano wersję deweloperską)
pytest

# Sprawdź formatowanie kodu (jeśli zainstalowano wersję deweloperską)
black . --check
flake8
mypy .
```

### 6. Uruchomienie gry

```bash
# Bezpośrednio z modułu
python -m main2048

# Lub jeśli zainstalowano przez setup.py
game2048
```

### 7. Deaktywacja środowiska

Gdy skończysz pracę z grą, możesz deaktywować środowisko wirtualne:
```bash
deactivate
```

## Rozwiązywanie problemów z instalacją

### Problemy z bibliotekami
Jeśli występują problemy z instalacją bibliotek:
1. Upewnij się, że używasz najnowszej wersji pip
2. Sprawdź czy masz zainstalowane wymagane narzędzia systemowe
3. W razie problemów z matplotlib na Linux, zainstaluj:
   ```bash
   sudo apt-get install python3-tk
   ```

### Problemy z kolorami w terminalu
1. Windows: Użyj Windows Terminal zamiast standardowego cmd.exe
2. Linux/macOS: Upewnij się, że terminal obsługuje kolory ANSI

### Problemy z prawami dostępu
1. Windows: Uruchom terminal jako administrator
2. Linux/macOS: Użyj sudo dla instalacji systemowych bibliotek

## Argumenty wiersza poleceń

Gra obsługuje następujące argumenty wiersza poleceń:

```bash
python -m main2048 [opcje]
```

Dostępne opcje:
- `--mode {classic,ai,time,obstacles,challenge,two_player}`: Wybór trybu gry (domyślnie: classic)
- `--size {3,4,5,6}`: Rozmiar planszy NxN (domyślnie: 4)
- `--target {1024,2048,4096}`: Wartość docelowa do wygrania (domyślnie: 2048)
- `--load PLIK`: Wczytaj zapisaną grę z podanego pliku
- `--no-color`: Wyłącz kolorowanie terminala
- `--debug`: Włącz tryb debugowania
- `--help`: Wyświetl pomoc i dostępne opcje

Przykłady użycia:
```bash
# Uruchom grę w trybie klasycznym z planszą 5x5
python -m main2048 --mode classic --size 5

# Uruchom grę z AI i wartością docelową 4096
python -m main2048 --mode ai --target 4096

# Wczytaj zapisaną grę
python -m main2048 --load save_game.json

# Tryb czasowy bez kolorów w terminalu
python -m main2048 --mode time --no-color
```

## Sterowanie
- Strzałki (↑ ↓ ← →) lub WASD: Przesuwanie kafelków
- U: Cofnij ruch
- R: Restart gry
- Q: Wyjście
- H: Pomoc
- ESC: Menu

## Tryby gry

### Klasyczny
Standardowa wersja gry 2048. Łącz kafelki, aby osiągnąć wartość 2048.

### Gra z AI
Pozwól AI pokazać najlepsze ruchy.

### Tryb czasowy
Wykonuj ruchy przed upływem czasu. Każdy ruch dodaje dodatkowy czas.

### Tryb z przeszkodami
Dodatkowe wyzwanie w postaci zablokowanych pól na planszy.

### Tryb wyzwań
Specjalne poziomy z określonymi celami do osiągnięcia.

### Gra dwuosobowa
Rywalizuj z innym graczem na podzielonym ekranie.

## Zapisywanie gry
- Automatyczny zapis co 5 minut
- Możliwość ręcznego zapisywania 
- System punktów kontrolnych
- Eksport i import stanu gry

## Statystyki
- Śledzenie najlepszych wyników
- Wykresy postępu
- Statystyki ruchów
- Historia gier

## Rozwiązywanie problemów

### Baza danych
Jeśli wystąpią problemy z bazą danych:
1. Zamknij grę
2. Usuń plik `game.db`
3. Uruchom ponownie grę - baza zostanie utworzona automatycznie

### Pliki zapisu
Jeśli plik zapisu jest uszkodzony:
1. Gra automatycznie spróbuje wczytać kopię zapasową
2. Jeśli to nie pomoże, usuń uszkodzony plik i użyj wcześniejszego zapisu z katalogu `backups/`

