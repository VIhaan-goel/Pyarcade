"""All calls from the frontend to the Flask API live here."""
import httpx

from config import BACKEND_URL

_client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=10)


class ApiError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


async def _request(method, path, json=None):
    try:
        response = await _client.request(method, path, json=json)
    except httpx.HTTPError as exc:
        raise ApiError(f"Cannot reach the backend at {BACKEND_URL} ({type(exc).__name__})") from exc
    try:
        data = response.json()
    except ValueError:
        data = None
    if response.status_code >= 400:
        message = data.get("error") if isinstance(data, dict) else None
        raise ApiError(message or f"Request failed ({response.status_code})", response.status_code)
    return data


async def list_games():
    return await _request("GET", "/api/games")


async def get_game(game_id):
    return await _request("GET", f"/api/games/{game_id}")


async def create_session(game_id):
    return await _request("POST", "/api/sessions", {"game_id": game_id})


async def get_session(session_id):
    return await _request("GET", f"/api/sessions/{session_id}")


async def send_input(session_id, events):
    return await _request("POST", f"/api/sessions/{session_id}/input", {"events": events})


async def stop_session(session_id):
    return await _request("DELETE", f"/api/sessions/{session_id}")
