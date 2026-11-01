from nicegui import app, ui

import auth
import theme  # noqa: F401  (registers fonts and styles)


def logout():
    app.storage.user.clear()
    ui.navigate.to("/")


def navbar():
    """Fixed top bar, separate from the page body. Call it at the top level of a page function."""
    user = auth.current_user()
    with ui.header().classes("pa-nav"):
        with ui.element("div").classes("pa-nav-inner"):
            ui.link("PyArcade", "/").classes("pa-small-logo")
            with ui.element("div").classes("pa-nav-right"):
                if user:
                    with ui.button(user["username"], icon="account_circle").props("flat no-caps").classes("pa-user"):
                        with ui.menu():
                            ui.menu_item(f"Player ID: PA-{auth.short_id(user['id'])}").props("disable")
                            ui.separator()
                            ui.menu_item("Sign out", on_click=logout)
                else:
                    ui.link("Sign in", "/login").classes("pa-nav-link")
                    ui.link("Sign up", "/signup").classes("pa-nav-cta")