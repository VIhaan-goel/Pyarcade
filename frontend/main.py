"""Python frontend (NiceGUI).   Run:  python main.py   then open http://localhost:8080"""
from pathlib import Path

from nicegui import app, ui

import config
from pages import account, home, play  # noqa: F401  (importing registers the pages)

app.add_static_files("/static", Path(__file__).parent / "static")

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PyArcade", host="0.0.0.0", port=config.PORT, reload=True, show=False, dark=True, favicon="🕹️", storage_secret=config.STORAGE_SECRET)
