from nicegui import ui

import api_client
import theme  # noqa: F401  (registers fonts and styles)
from api_client import ApiError
from navbar import navbar


@ui.page("/")
async def home():
    ui.page_title("PyArcade")
    navbar()
    with ui.column().classes("pa-wrap"):
        ui.label("PyArcade").classes("pa-logo")
        ui.label("Six games written in Python. They run on the server and play right here in your browser.").classes("pa-tagline")
        ui.label("Pick a game").classes("pa-section")

        with ui.element("div").classes("pa-list"):
            try:
                games = await api_client.list_games()
            except ApiError as exc:
                ui.label(f"Could not load games: {exc}. Check that the backend is running and BACKEND_URL is correct.").classes("pa-notice")
                return

            for i, game in enumerate(games):
                with ui.link(target=f"/play/{game['id']}").classes("pa-card").style(f"--accent: {game['accent']}; --i: {i}"):
                    ui.label(game["icon"]).classes("pa-icon")
                    with ui.column().classes("pa-text"):
                        ui.label(game["title"]).classes("pa-title")
                        ui.label(game["description"]).classes("pa-desc")
                        ui.label("  ·  ".join(f"{c['keys']}" for c in game["controls"][:2])).classes("pa-keys")
                    ui.label("Play").classes("pa-cta")
                    
