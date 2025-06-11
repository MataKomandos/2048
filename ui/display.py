from typing import List, Optional, Dict, Tuple, Union
import os
from colorama import init, Fore, Back, Style
from .animations import Animations
from .theme_manager import ThemeManager

init(convert=True)

class Display:
    def __init__(self):
        self.theme_manager = ThemeManager()
    
    @staticmethod
    def clear_screen() -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def display_board(board: List[List[Union[int, str]]], score: int, player_nickname: str,
                     theme_colors: Optional[Dict] = None, difficulty: Optional[str] = None,
                     can_undo: bool = False, remaining_undos: Optional[int] = None) -> None:
        Display.clear_screen()
        print(f"\n{Fore.GREEN}Gracz: {player_nickname}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Wynik: {score}{Style.RESET_ALL}")
        
        if difficulty is not None:
            print(f"{Fore.YELLOW}Poziom trudności: {difficulty}{Style.RESET_ALL}")
        
        if remaining_undos is not None:
            print(f"{Fore.MAGENTA}Pozostałe cofnięcia/podpowiedzi: {remaining_undos}{Style.RESET_ALL}")
        
        print()
        
        size = len(board)
        max_width = max(len(str(cell)) for row in board for cell in row if cell != 'X' and cell != 0)
        cell_width = max(8, max_width + 2)
        
        separator = "+" + ("-" * cell_width + "+") * size
        
        for row in board:
            print(separator)
            print("|", end="")
            for cell in row:
                if cell == 'X':
                    cell_str = f"{Fore.WHITE}{Back.RED}{'X'.center(cell_width)}{Style.RESET_ALL}"
                elif cell == 0:
                    cell_str = " " * cell_width
                else:
                    fore_color = Fore.WHITE
                    back_color = Back.BLACK
                    if theme_colors and str(cell) in theme_colors:
                        fore_color, back_color = theme_colors[str(cell)]
                    
                    cell_str = f"{fore_color}{back_color}{str(cell).center(cell_width)}{Style.RESET_ALL}"
                print(f"{cell_str}|", end="")
            print()
        print(separator + "\n")

        controls = ["Strzałki = Ruch", "R = Restart", "Q = Wyjście", "H = Pomoc"]
        if can_undo:
            controls.append("Z = Cofnij")
        print(f"{Fore.YELLOW}{' | '.join(controls)}{Style.RESET_ALL}\n")
    
    def display_theme_menu(self) -> None:
        while True:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== USTAWIENIA MOTYWU ==={Style.RESET_ALL}")
            print(f"\nAktualny motyw: {self.theme_manager.current_theme}")
            print("\n1. Wybierz gotowy motyw")
            print("2. Stwórz własny motyw")
            print("3. Usuń własny motyw")
            print("4. Powrót\n")
            
            choice = input("Wybierz opcję (1-4): ")
            
            if choice == "1":
                self._display_theme_selection()
            elif choice == "2":
                self._create_custom_theme()
            elif choice == "3":
                self._delete_custom_theme()
            elif choice == "4":
                break
    
    def _display_theme_selection(self) -> None:
        while True:
            self.clear_screen()
            print(f"\n{Fore.CYAN}=== WYBÓR MOTYWU ==={Style.RESET_ALL}\n")
            themes = self.theme_manager.get_available_themes()
            
            for i, theme in enumerate(themes, 1):
                print(f"{i}. {theme}")
            print(f"{len(themes) + 1}. Powrót\n")
            
            try:
                choice = int(input(f"Wybierz motyw (1-{len(themes) + 1}): "))
                if 1 <= choice <= len(themes):
                    self.theme_manager.set_theme(themes[choice - 1])
                    print("\nMotyw został zmieniony!")
                    input("\nNaciśnij Enter, aby kontynuować...")
                elif choice == len(themes) + 1:
                    break
            except ValueError:
                print("\nNieprawidłowy wybór!")
                input("\nNaciśnij Enter, aby kontynuować...")
    
    def _create_custom_theme(self) -> None:
        self.clear_screen()
        print(f"\n{Fore.CYAN}=== TWORZENIE WŁASNEGO MOTYWU ==={Style.RESET_ALL}\n")
        
        name = input("Podaj nazwę motywu: ")
        if name in self.theme_manager.DEFAULT_THEMES:
            print("\nNie można nadpisać motywu domyślnego!")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
        
        print("\nDostępne kolory tekstu:")
        fore_colors = [attr for attr in dir(Fore) if not attr.startswith('_')]
        for i, color in enumerate(fore_colors, 1):
            print(f"{i}. {color}")
        
        print("\nDostępne kolory tła:")
        back_colors = [attr for attr in dir(Back) if not attr.startswith('_')]
        for i, color in enumerate(back_colors, 1):
            print(f"{i}. {color}")
        
        theme_colors = {}
        values = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        
        for value in values:
            print(f"\nWybierz kolory dla {value}:")
            try:
                fore_idx = int(input(f"Wybierz kolor tekstu (1-{len(fore_colors)}): ")) - 1
                back_idx = int(input(f"Wybierz kolor tła (1-{len(back_colors)}): ")) - 1
                
                if 0 <= fore_idx < len(fore_colors) and 0 <= back_idx < len(back_colors):
                    theme_colors[str(value)] = (
                        getattr(Fore, fore_colors[fore_idx]),
                        getattr(Back, back_colors[back_idx])
                    )
                else:
                    print("\nNieprawidłowy wybór!")
                    return
            except ValueError:
                print("\nNieprawidłowy wybór!")
                return
        
        theme_colors["0"] = (Fore.BLACK, Back.BLACK)
        
        if self.theme_manager.add_custom_theme(name, theme_colors):
            print("\nMotyw został utworzony!")
        else:
            print("\nMotyw o tej nazwie już istnieje!")
        
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def _delete_custom_theme(self) -> None:
        self.clear_screen()
        print(f"\n{Fore.CYAN}=== USUWANIE WŁASNEGO MOTYWU ==={Style.RESET_ALL}\n")
        
        custom_themes = [theme for theme in self.theme_manager.get_available_themes()
                        if theme not in self.theme_manager.DEFAULT_THEMES]
        
        if not custom_themes:
            print("Brak własnych motywów do usunięcia!")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
        
        print("Dostępne własne motywy:")
        for i, theme in enumerate(custom_themes, 1):
            print(f"{i}. {theme}")
        print(f"{len(custom_themes) + 1}. Anuluj\n")
        
        try:
            choice = int(input(f"Wybierz motyw do usunięcia (1-{len(custom_themes) + 1}): "))
            if 1 <= choice <= len(custom_themes):
                theme_name = custom_themes[choice - 1]
                if self.theme_manager.delete_theme(theme_name):
                    print(f"\nMotyw {theme_name} został usunięty!")
                else:
                    print("\nNie można usunąć tego motywu!")
            elif choice == len(custom_themes) + 1:
                return
        except ValueError:
            print("\nNieprawidłowy wybór!")
        
        input("\nNaciśnij Enter, aby kontynuować...")
    
    @staticmethod
    def display_menu() -> None:
        Display.clear_screen()
        print(f"\n{Fore.CYAN}=== 2048 ==={Style.RESET_ALL}")
        print("\n1. Nowa gra")
        print("2. Kontynuuj")
        print("3. Najlepsze wyniki")
        print("4. Ustawienia")
        print("5. Zapisy i checkpointy")
        print("6. Pomoc")
        print("7. Wyjście\n")
        print("Użyj klawiszy numerycznych (1-7) aby wybrać opcję\n")
    
    @staticmethod
    def display_controls() -> None:
        Display.clear_screen()
        print(f"\n{Fore.YELLOW}=== STEROWANIE ==={Style.RESET_ALL}")
        print("\nSterowanie w grze:")
        print("↑ = Ruch w górę")
        print("↓ = Ruch w dół")
        print("← = Ruch w lewo")
        print("→ = Ruch w prawo")
        print("Q = Wyjście z gry")
        print("R = Restart gry")
        print("H = Pokaż pomoc")
        print("\nNaciśnij dowolny klawisz, aby wrócić do gry...")
    
    @staticmethod
    def display_game_over(score: int) -> None:
        print(f"\n{Fore.RED}Koniec gry!{Style.RESET_ALL}")
        print(f"Końcowy wynik: {score}")
        print("\nNaciśnij dowolny klawisz, aby kontynuować...")
    
    @staticmethod
    def display_win(score: int) -> None:
        print(f"\n{Fore.GREEN}Gratulacje! Osiągnąłeś 2048!{Style.RESET_ALL}")
        print(f"Wynik: {score}")
        print("Możesz kontynuować grę, aby osiągnąć wyższy wynik!")
        print("\nNaciśnij dowolny klawisz, aby kontynuować...") 