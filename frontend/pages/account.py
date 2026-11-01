from urllib.parse import quote

from nicegui import app, run, ui
from starlette.responses import RedirectResponse

import auth
import theme  # noqa: F401  (registers fonts and styles)
from navbar import navbar


def _safe_next(target):
    """Only allow redirects to pages on this site (blocks links like //evil.com)."""
    return target if target.startswith("/") and not target.startswith("//") and "\\" not in target else "/"


@ui.page("/login")
async def login_page(next: str = "/"):
    destination = _safe_next(next)
    if auth.current_user():
        return RedirectResponse(destination)

    ui.page_title("Sign in | PyArcade")
    ui.colors(primary="#7c5cff")
    navbar()

    async def submit():
        error.set_text("")
        submit_btn.props("loading")
        user_id = await run.io_bound(auth.authenticate, identifier.value, password.value)
        submit_btn.props(remove="loading")
        if not user_id:
            error.set_text("Wrong username/email or password.")
            return
        app.storage.user["user_id"] = user_id
        ui.navigate.to(destination)

    with ui.column().classes("pa-auth-wrap"):
        with ui.column().classes("pa-auth-card"):
            ui.label("Welcome back").classes("pa-auth-title")
            ui.label("Sign in to your PyArcade account.").classes("pa-auth-sub")
            identifier = ui.input("Username or email").props('outlined autocomplete="username"').classes("w-full")
            password = ui.input("Password", password=True, password_toggle_button=True) \
                .props('outlined autocomplete="current-password"').classes("w-full")
            password.on("keydown.enter", submit)
            error = ui.label().classes("pa-error")
            submit_btn = ui.button("Sign in", on_click=submit).classes("pa-btn w-full").props("no-caps unelevated")
            with ui.row().classes("pa-auth-alt"):
                ui.label("New here?")
                ui.link("Create an account", f"/signup?next={quote(destination)}")


@ui.page("/signup")
async def signup_page(next: str = "/"):
    destination = _safe_next(next)
    if auth.current_user():
        return RedirectResponse(destination)

    ui.page_title("Sign up | PyArcade")
    ui.colors(primary="#7c5cff")
    navbar()

    async def submit():
        error.set_text("")
        if password.value != confirm.value:
            error.set_text("Passwords do not match.")
            return
        submit_btn.props("loading")
        try:
            user_id = await run.io_bound(auth.create_user, username.value, email.value, password.value)
        except auth.AuthError as exc:
            error.set_text(str(exc))
            return
        finally:
            submit_btn.props(remove="loading")
        app.storage.user["user_id"] = user_id  # sign the new player in straight away
        ui.navigate.to(destination)

    with ui.column().classes("pa-auth-wrap"):
        with ui.column().classes("pa-auth-card"):
            ui.label("Create account").classes("pa-auth-title")
            ui.label("Get your own player ID in a few seconds.").classes("pa-auth-sub")
            username = ui.input("Username").props('outlined autocomplete="username"').classes("w-full")
            email = ui.input("Email").props('outlined type="email" autocomplete="email"').classes("w-full")
            password = ui.input("Password", password=True, password_toggle_button=True) \
                .props('outlined autocomplete="new-password"').classes("w-full")
            confirm = ui.input("Confirm password", password=True) \
                .props('outlined autocomplete="new-password"').classes("w-full")
            confirm.on("keydown.enter", submit)
            error = ui.label().classes("pa-error")
            submit_btn = ui.button("Sign up", on_click=submit).classes("pa-btn w-full").props("no-caps unelevated")
            with ui.row().classes("pa-auth-alt"):
                ui.label("Already have an account?")
                ui.link("Sign in", f"/login?next={quote(destination)}")