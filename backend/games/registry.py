"""List of games shown on the website.

To add a new pygame game: drop the .py file into this folder (it must start itself with
`if __name__ == "__main__": main()`), then add one entry below. Nothing else changes.
"""
from pathlib import Path

GAMES_DIR = Path(__file__).resolve().parent

GAMES = [
    {
        "id": "snake",
        "title": "Snake",
        "description": "Eat the food, grow longer, don't hit a wall or yourself.",
        "file": "snake.py",
        "icon": "🐍",
        "accent": "#4ade80",
        "controls": [
            {"keys": "Arrow keys / WASD", "action": "Steer"},
            {"keys": "Space", "action": "Pause"},
            {"keys": "R", "action": "Restart"},
        ],
    },
    {
        "id": "pacman",
        "title": "Pac-Man",
        "description": "Clear the maze, grab power pellets, outrun the ghosts.",
        "file": "pacman.py",
        "icon": "👻",
        "accent": "#facc15",
        "controls": [
            {"keys": "Arrow keys / WASD", "action": "Move"},
            {"keys": "Space", "action": "Pause"},
            {"keys": "R", "action": "Restart"},
        ],
    },
    {
        "id": "chess",
        "title": "Chess",
        "description": "Play white against a simple AI, or switch to two players.",
        "file": "chess_game.py",
        "icon": "♟️",
        "accent": "#a3e635",
        "controls": [
            {"keys": "Click", "action": "Select and move a piece"},
            {"keys": "A", "action": "Switch AI / 2-player"},
            {"keys": "R", "action": "Restart"},
        ],
    },
    {
        "id": "dino",
        "title": "Dino Run",
        "description": "Jump cacti and duck under birds in the desert.",
        "file": "dino_run.py",
        "icon": "🦖",
        "accent": "#94a3b8",
        "controls": [
            {"keys": "Space / Up", "action": "Jump"},
            {"keys": "Down / S", "action": "Duck"},
            {"keys": "R", "action": "Restart"},
        ],
    },
    {
        "id": "flappy",
        "title": "Flappy Bird",
        "description": "Tap to flap through the pipes without touching them.",
        "file": "flappy_bird.py",
        "icon": "🐦",
        "accent": "#38bdf8",
        "controls": [
            {"keys": "Space / Up / Click", "action": "Flap"},
            {"keys": "R", "action": "Restart"},
        ],
    },
    {
        "id": "racing",
        "title": "Highway Racing",
        "description": "Weave through traffic as the road gets faster.",
        "file": "car_racing.py",
        "icon": "🏎️",
        "accent": "#f87171",
        "controls": [
            {"keys": "Left / Right or A / D", "action": "Change lane"},
            {"keys": "R", "action": "Restart after a crash"},
        ],
    },
    {
        "id": "2048",
        "title": "2048",
        "description": "Merge matching number tiles, build bigger numbers, and reach the legendary 2048 tile.",
        "file": "2048.py",
        "icon": "🔢",
        "accent": "#edc22e",
        "controls": [
            {"keys": "Arrow Keys / WASD", "action": "Move Tiles"},
            {"keys": "R", "action": "Restart Game"},
        ],
    },
    {
        "id": "tictactoe",
        "title": "Tic Tac Toe",
        "description": "Challenge a friend or the computer in this classic X and O strategy game. Get three in a row to win!",
        "file": "tictactoe.py",
        "icon": "⭕",
        "accent": "#89b4fa",
        "controls": [
            {"keys": "Mouse Click", "action": "Place X / O"},
            {"keys": "New Round", "action": "Restart Round"},
            {"keys": "Menu", "action": "Change Game Mode"},
        ],
    },  
]

_BY_ID = {g["id"]: g for g in GAMES}


def get_game(game_id):
    return _BY_ID.get(game_id)


def game_path(game):
    return str(GAMES_DIR / game["file"])


def public_view(game):
    """What the API returns (never exposes file paths)."""
    return {k: v for k, v in game.items() if k != "file"}
