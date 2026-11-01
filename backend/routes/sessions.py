import time

from flask import Blueprint, Response, jsonify, request, stream_with_context

import config
from games.registry import game_path, get_game
from services.session_manager import CapacityError, manager

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")

ALLOWED_TYPES = {"keydown", "keyup", "mousedown", "mouseup", "release_all", "quit"}
MAX_EVENTS_PER_REQUEST = 20


def _clean_event(raw):
    """Validate one input event from the browser. Returns a safe dict or None."""
    if not isinstance(raw, dict) or raw.get("type") not in ALLOWED_TYPES:
        return None
    event = {"type": raw["type"]}
    if raw["type"] in ("keydown", "keyup"):
        code = raw.get("code")
        if not isinstance(code, str) or len(code) > 16:
            return None
        event["code"] = code
    elif raw["type"] in ("mousedown", "mouseup"):
        try:
            event["x"] = max(0, min(5000, int(raw.get("x", 0))))
            event["y"] = max(0, min(5000, int(raw.get("y", 0))))
        except (TypeError, ValueError):
            return None
    return event


@bp.post("")
def create_session():
    """POST /api/sessions  {"game_id": "snake"} -> starts a game for this player."""
    body = request.get_json(silent=True) or {}
    game = get_game(body.get("game_id"))
    if game is None:
        return jsonify({"error": "Unknown game_id"}), 400
    try:
        session = manager.create(game, game_path(game))
    except CapacityError as exc:
        return jsonify({"error": str(exc)}), 503
    return jsonify(session.describe()), 201


@bp.get("/<session_id>")
def session_status(session_id):
    """GET /api/sessions/<id> -> is the game still running?"""
    session = manager.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found or expired"}), 404
    return jsonify(session.describe())


@bp.post("/<session_id>/input")
def session_input(session_id):
    """POST /api/sessions/<id>/input  {"events": [{"type": "keydown", "code": "ArrowLeft"}]}"""
    session = manager.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found or expired"}), 404
    body = request.get_json(force=True, silent=True)
    if body is None:
        return jsonify({"error": "JSON body required"}), 400
    raw_events = body.get("events") if isinstance(body, dict) and "events" in body else [body]
    if not isinstance(raw_events, list):
        return jsonify({"error": "events must be a list"}), 400
    events = [e for e in (_clean_event(r) for r in raw_events[:MAX_EVENTS_PER_REQUEST]) if e]
    if not events:
        return jsonify({"error": "No valid events"}), 400
    if not session.send_events(events):
        return jsonify({"error": "Game has ended"}), 410
    return jsonify({"accepted": len(events)}), 202


@bp.get("/<session_id>/stream")
def session_stream(session_id):
    """GET /api/sessions/<id>/stream -> live video of the game (MJPEG, use it as <img src>)."""
    session = manager.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found or expired"}), 404

    def generate():
        last_id = 0
        while True:
            session.touch_viewer()
            frame_id, frame, ended = session.wait_for_frame(last_id, timeout=1.0)
            if frame is not None and frame_id != last_id:
                last_id = frame_id
                mime = b"image/jpeg" if frame[:2] == b"\xff\xd8" else b"image/png"
                yield (
                    b"--frame\r\nContent-Type: " + mime +
                    b"\r\nContent-Length: " + str(len(frame)).encode() + b"\r\n\r\n" +
                    frame + b"\r\n"
                )
            if ended:
                return

    return Response(
        stream_with_context(generate()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


def _stop(session_id):
    if manager.stop(session_id):
        return jsonify({"stopped": True})
    return jsonify({"error": "Session not found or expired"}), 404


@bp.delete("/<session_id>")
def delete_session(session_id):
    """DELETE /api/sessions/<id> -> stop the game."""
    return _stop(session_id)


@bp.post("/<session_id>/stop")
def stop_session_post(session_id):
    """POST /api/sessions/<id>/stop -> same as DELETE (browsers can send this on page close)."""
    return _stop(session_id)
