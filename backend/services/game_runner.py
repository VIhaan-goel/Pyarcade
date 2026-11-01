"""Runs ONE pygame game in a headless process and talks to the Flask server through pipes.

    python game_runner.py <path/to/game.py>

stdin  <- JSON lines from the server, e.g. {"type": "keydown", "code": "ArrowLeft"}
stdout -> frames: 4-byte big-endian length followed by that many bytes of JPEG/PNG data

The game file itself is NOT modified. We only replace four pygame functions
(display.flip, event.get, event.pump, key.get_pressed) so that the game draws into
an invisible window and reads its input from the pipe instead of a real keyboard.
"""
import io
import json
import os
import queue
import runpy
import struct
import sys
import threading
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa: E402  (must come after the environment variables above)

# Keep the real stdout for frames; anything the game prints goes to stderr (server log).
_frame_out = sys.stdout.buffer
sys.stdout = sys.stderr

STREAM_FPS = max(1, int(os.environ.get("STREAM_FPS", "30")))
FRAME_FORMAT = os.environ.get("FRAME_FORMAT", "jpg").lower()
MIN_INTERVAL = 0.9 / STREAM_FPS

_events = queue.Queue()
_pressed = set()

SPECIAL_KEYS = {
    "ArrowUp": pygame.K_UP,
    "ArrowDown": pygame.K_DOWN,
    "ArrowLeft": pygame.K_LEFT,
    "ArrowRight": pygame.K_RIGHT,
    "Space": pygame.K_SPACE,
    "Enter": pygame.K_RETURN,
    "Escape": pygame.K_ESCAPE,
    "ShiftLeft": pygame.K_LSHIFT,
    "ShiftRight": pygame.K_RSHIFT,
}


def code_to_key(code):
    """Browser KeyboardEvent.code -> pygame key constant (or None)."""
    if code in SPECIAL_KEYS:
        return SPECIAL_KEYS[code]
    if isinstance(code, str) and len(code) == 4 and code.startswith("Key"):
        return getattr(pygame, "K_" + code[3].lower(), None)
    return None


def handle_message(msg):
    kind = msg.get("type")
    if kind in ("keydown", "keyup"):
        key = code_to_key(msg.get("code"))
        if key is None:
            return
        if kind == "keydown":
            _pressed.add(key)
            _events.put(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode=""))
        else:
            _pressed.discard(key)
            _events.put(pygame.event.Event(pygame.KEYUP, key=key, mod=0))
    elif kind in ("mousedown", "mouseup"):
        pos = (int(msg.get("x", 0)), int(msg.get("y", 0)))
        etype = pygame.MOUSEBUTTONDOWN if kind == "mousedown" else pygame.MOUSEBUTTONUP
        _events.put(pygame.event.Event(etype, pos=pos, button=1))
    elif kind == "release_all":
        for key in list(_pressed):
            _pressed.discard(key)
            _events.put(pygame.event.Event(pygame.KEYUP, key=key, mod=0))
    elif kind == "quit":
        _events.put(pygame.event.Event(pygame.QUIT))


def stdin_reader():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle_message(json.loads(line))
        except Exception as exc:  # a bad message must never crash the game
            print("bad input message:", exc, file=sys.stderr)
    _events.put(pygame.event.Event(pygame.QUIT))  # server closed the pipe


class _Pressed:
    """Stands in for pygame.key.get_pressed(): supports keys[pygame.K_LEFT]."""

    def __getitem__(self, key):
        return key in _pressed


def fake_event_get(*_args, **_kwargs):
    items = []
    try:
        while True:
            items.append(_events.get_nowait())
    except queue.Empty:
        pass
    return items


def encode_frame(surface):
    buf = io.BytesIO()
    if FRAME_FORMAT == "png":
        pygame.image.save(surface, buf, "frame.png")
    else:
        try:
            pygame.image.save(surface, buf, "frame.jpg")
        except Exception:
            buf = io.BytesIO()
            pygame.image.save(surface, buf, "frame.png")
    return buf.getvalue()


_real_flip = pygame.display.flip
_last_sent = [0.0]


def fake_flip():
    _real_flip()
    now = time.monotonic()
    if now - _last_sent[0] < MIN_INTERVAL:
        return
    surface = pygame.display.get_surface()
    if surface is None:
        return
    data = encode_frame(surface)
    try:
        _frame_out.write(struct.pack(">I", len(data)))
        _frame_out.write(data)
        _frame_out.flush()
    except (BrokenPipeError, OSError):
        os._exit(0)  # the server is gone, nothing left to do
    _last_sent[0] = now


def main():
    if len(sys.argv) != 2:
        print("usage: game_runner.py <game.py>", file=sys.stderr)
        sys.exit(2)
    game_file = sys.argv[1]

    pygame.display.flip = fake_flip
    pygame.event.get = fake_event_get
    pygame.event.pump = lambda: None
    pygame.key.get_pressed = lambda: _Pressed()

    threading.Thread(target=stdin_reader, daemon=True).start()

    game_dir = os.path.dirname(os.path.abspath(game_file))
    sys.path.insert(0, game_dir)
    runpy.run_path(game_file, run_name="__main__")


if __name__ == "__main__":
    main()
