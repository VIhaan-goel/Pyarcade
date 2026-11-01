"""Starts, tracks and stops running games.

One session = one Python subprocess (game_runner.py) that runs one game for one player.
Processes keep the games isolated: one player's game can never affect another's.
"""
import json
import os
import struct
import subprocess
import sys
import threading
import time
import uuid

import config


class CapacityError(Exception):
    """Too many games are running at the moment."""


def _read_exact(stream, size):
    data = b""
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


class GameSession:
    def __init__(self, session_id, game, process):
        self.id = session_id
        self.game = game
        self.process = process
        self.created_at = time.time()
        self.last_input = time.time()
        self.last_viewer = time.time()
        self._cond = threading.Condition()
        self._frame = None
        self._frame_id = 0
        self._ended = False
        self._stdin_lock = threading.Lock()
        threading.Thread(target=self._read_frames, daemon=True).start()

    # ---- frames -------------------------------------------------------------
    def _read_frames(self):
        out = self.process.stdout
        try:
            while True:
                header = _read_exact(out, 4)
                if header is None:
                    break
                (size,) = struct.unpack(">I", header)
                data = _read_exact(out, size)
                if data is None:
                    break
                with self._cond:
                    self._frame = data
                    self._frame_id += 1
                    self._cond.notify_all()
        finally:
            with self._cond:
                self._ended = True
                self._cond.notify_all()

    def wait_for_frame(self, last_id, timeout=1.0):
        """Block until a newer frame exists. Returns (frame_id, frame_bytes, ended)."""
        with self._cond:
            self._cond.wait_for(lambda: self._frame_id != last_id or self._ended, timeout)
            return self._frame_id, self._frame, self._ended

    # ---- input --------------------------------------------------------------
    def send_events(self, events):
        self.last_input = time.time()
        payload = "".join(json.dumps(e) + "\n" for e in events).encode()
        with self._stdin_lock:
            try:
                self.process.stdin.write(payload)
                self.process.stdin.flush()
                return True
            except (BrokenPipeError, OSError, ValueError):
                return False

    # ---- state --------------------------------------------------------------
    @property
    def running(self):
        return self.process.poll() is None

    def touch_viewer(self):
        self.last_viewer = time.time()

    def describe(self):
        return {
            "session_id": self.id,
            "game_id": self.game["id"],
            "running": self.running,
            "uptime_seconds": int(time.time() - self.created_at),
            "stream_url": f"/api/sessions/{self.id}/stream",
            "input_url": f"/api/sessions/{self.id}/input",
        }

    def stop(self):
        try:
            self.process.stdin.close()
        except Exception:
            pass
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        try:
            self.process.stdout.close()
        except Exception:
            pass


class SessionManager:
    def __init__(self):
        self._sessions = {}
        self._lock = threading.Lock()
        self._reaper_started = False

    def create(self, game, game_file):
        self._start_reaper()
        with self._lock:
            if len(self._sessions) >= config.MAX_SESSIONS:
                raise CapacityError("Server is full, try again in a minute.")
            env = {
                "STREAM_FPS": str(config.STREAM_FPS),
                "FRAME_FORMAT": config.FRAME_FORMAT,
            }
            process = subprocess.Popen(
                [sys.executable, config.RUNNER_PATH, game_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=None,  # runner/game errors show up in the server log
                env={**os.environ, **env},
                close_fds=True,
            )
            session = GameSession(uuid.uuid4().hex, game, process)
            self._sessions[session.id] = session
            return session

    def get(self, session_id):
        with self._lock:
            return self._sessions.get(session_id)

    def stop(self, session_id):
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if session:
            session.stop()
            return True
        return False

    def count(self):
        with self._lock:
            return len(self._sessions)

    def _start_reaper(self):
        if self._reaper_started:
            return
        self._reaper_started = True
        threading.Thread(target=self._reap_loop, daemon=True).start()

    def _reap_loop(self):
        while True:
            time.sleep(5)
            now = time.time()
            with self._lock:
                stale = [
                    sid for sid, s in self._sessions.items()
                    if not s.running
                    or now - s.last_viewer > config.NO_VIEWER_TIMEOUT
                    or now - s.last_input > config.IDLE_INPUT_TIMEOUT
                ]
            for sid in stale:
                self.stop(sid)


manager = SessionManager()
