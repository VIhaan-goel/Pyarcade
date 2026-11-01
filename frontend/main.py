"""Python frontend (NiceGUI).   Run:  python main.py   then open http://localhost:8080"""
from nicegui import ui

import config
from pages import account, home, play  # noqa: F401  (importing registers the pages)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="PyArcade", host="0.0.0.0", port=config.PORT, reload=True, show=False, dark=True, favicon="🕹️", storage_secret=config.STORAGE_SECRET)