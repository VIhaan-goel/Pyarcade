from flask import Blueprint, jsonify

from games.registry import GAMES, get_game, public_view

bp = Blueprint("games", __name__, url_prefix="/api/games")


@bp.get("")
def list_games():
    """GET /api/games -> every game on the site."""
    return jsonify([public_view(g) for g in GAMES])


@bp.get("/<game_id>")
def get_one_game(game_id):
    """GET /api/games/<id> -> one game (title, description, controls)."""
    game = get_game(game_id)
    if game is None:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(public_view(game))
