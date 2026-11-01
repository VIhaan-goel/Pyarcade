from nicegui import ui

import api_client
import theme  # noqa: F401  (registers fonts and styles)
from api_client import ApiError
from config import PUBLIC_BACKEND_URL
from navbar import navbar

# The only JavaScript in the project: sends key presses straight to the Flask API.
# (It skips the NiceGUI server, which is what removes the lag.)
INPUT_JS = """
<script>
window.pyarcade = (() => {
  let url = null, chain = Promise.resolve();
  const KEY = /^(Arrow(Up|Down|Left|Right)|Space|Enter|Key[A-Z])$/;
  const send = (events) => {
    if (!url) return;
    const body = JSON.stringify({ events });
    chain = chain.then(() => fetch(url, { method: 'POST', mode: 'no-cors', keepalive: true,
      headers: { 'Content-Type': 'text/plain' }, body })).catch(() => {});
  };
  addEventListener('keydown', (e) => {
    if (!url || !KEY.test(e.code) || e.ctrlKey || e.metaKey || e.altKey) return;
    e.preventDefault();
    if (!e.repeat) send([{ type: 'keydown', code: e.code }]);
  });
  addEventListener('keyup', (e) => {
    if (!url || !KEY.test(e.code)) return;
    e.preventDefault();
    send([{ type: 'keyup', code: e.code }]);
  });
  addEventListener('blur', () => send([{ type: 'release_all' }]));
  return { start: (u) => { url = u; }, stop: () => { url = null; } };
})();
</script>
"""


@ui.page("/play/{game_id}")
async def play(game_id: str):
    try:
        game = await api_client.get_game(game_id)
    except ApiError as exc:
        with ui.column().classes("pa-wrap"):
            ui.label("PyArcade").classes("pa-small-logo")
            ui.label("That game does not exist." if exc.status == 404 else f"Could not reach the server: {exc}").classes("pa-notice")
            ui.link("Back to all games", "/")
        return

    ui.page_title(f"{game['title']} | PyArcade")
    ui.add_head_html(INPUT_JS)
    ui.add_css("html, body { overflow: hidden; }")  # stop arrow keys / space from scrolling the page
    state = {"sid": None, "queue": [], "sending": False}

    navbar()

    with ui.element("div").classes("pa-play").style(f"--accent: {game['accent']}"):
        with ui.column().classes("pa-stage"):
            ui.label(game["title"]).classes("pa-play-title")
            ui.label(game["description"]).classes("pa-play-desc")

            with ui.element("div").classes("pa-bezel"):
                with ui.element("div").classes("pa-screen"):
                    image = ui.interactive_image(on_mouse=lambda e: on_mouse(e), events=["mousedown"])
                    with ui.column().classes("pa-overlay") as overlay:
                        message = ui.label("Ready when you are.").classes("pa-msg") 
                        play_btn = ui.button("Play", on_click=lambda: start()).classes("pa-btn")

            stop_btn = ui.button("Stop game", on_click=lambda: stop()).classes("pa-ghost").props("flat no-caps")
            stop_btn.set_visibility(False)

        with ui.column().classes("pa-side"):
            ui.label("Controls").classes("pa-side-title")
            for control in game["controls"]:
                ui.label(control["keys"]).classes("pa-ctl-key")
                ui.label(control["action"]).classes("pa-ctl-act")
            ui.label("Click Play, then use your keyboard. Chess and Flappy Bird also accept mouse clicks on the screen.").classes("pa-note")

    # ---------- session lifecycle ----------
    async def start():
        play_btn.set_visibility(False)
        message.set_text("Starting game...")
        try:
            session = await api_client.create_session(game_id)
        except ApiError as exc:
            message.set_text(str(exc))
            play_btn.set_text("Try again")
            play_btn.set_visibility(True)
            return
        state["sid"] = session["session_id"]
        ui.run_javascript(f"window.pyarcade.start('{PUBLIC_BACKEND_URL}{session['input_url']}')")
        image.set_source(f"{PUBLIC_BACKEND_URL}{session['stream_url']}")
        overlay.classes(add="pa-hidden")
        stop_btn.set_visibility(True)

    def end(text):
        state["sid"] = None
        state["queue"].clear()
        ui.run_javascript("window.pyarcade.stop()")
        image.set_source("")
        stop_btn.set_visibility(False)
        message.set_text(text)
        play_btn.set_text("Play again")
        play_btn.set_visibility(True)
        overlay.classes(remove="pa-hidden")
        
    async def stop():
        sid = state["sid"]
        if not sid:
            return
        end("Game stopped.")
        try:
            await api_client.stop_session(sid)
        except ApiError:
            pass

    async def check_session():
        sid = state["sid"]
        if not sid:
            return
        try:
            info = await api_client.get_session(sid)
            if not info["running"]:
                end("The game closed.")
        except ApiError as exc:
            if exc.status == 404:
                end("Session ended (no activity for a while).")

    # ---------- mouse clicks (Chess, Flappy Bird) still go through Python ----------
    async def on_mouse(event):
        if not state["sid"]:
            return
        state["queue"].append({"type": "mousedown", "x": int(event.image_x), "y": int(event.image_y)})
        await flush()

    async def flush():
        if state["sending"]:
            return
        state["sending"] = True
        try:
            while state["queue"] and state["sid"]:
                batch = state["queue"][:20]
                del state["queue"][:20]
                try:
                    await api_client.send_input(state["sid"], batch)
                except ApiError as exc:
                    if exc.status in (404, 410):
                        end("The game has ended.")
                        break
        finally:
            state["sending"] = False

    ui.timer(3.0, check_session)

    async def cleanup():
        if state["sid"]:
            try:
                await api_client.stop_session(state["sid"])
            except ApiError:
                pass

    ui.context.client.on_disconnect(cleanup)