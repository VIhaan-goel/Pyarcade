import time

from flask import Blueprint, jsonify

import config
from games.registry import GAMES
from services.session_manager import manager

bp = Blueprint("health", __name__, url_prefix="/api")
_started = time.time()


@bp.get("/health")
def health():
    """GET /api/health -> used by the hosting platform to check the server is alive."""
    return jsonify({
        "status": "ok",
        "games": len(GAMES),
        "active_sessions": manager.count(),
        "max_sessions": config.MAX_SESSIONS,
        "uptime_seconds": int(time.time() - _started),
    })
