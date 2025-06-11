from core.database import DatabaseManager

db = DatabaseManager("game_data.db")

player = db.add_player("TestGracz")

game = db.start_game(player, "classic")

moves = ["up", "right", "down", "left"]
for move in moves:
    db.add_move(game, move, 4)

db.update_game(game, score=100, max_tile=64)
db.complete_game(game)

print("Baza danych została utworzona i wypełniona przykładowymi danymi!")
print("\nMożesz teraz użyć następujących zapytań SQL:")
print("\n1. SELECT * FROM players;")
print("2. SELECT * FROM games;")
print("3. SELECT * FROM moves;") 