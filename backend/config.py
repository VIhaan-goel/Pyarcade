"""Central configuration. Every value can be overridden with an environment variable."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Max number of games running at the same time (each one is a separate Python process).
MAX_SESSIONS = int(os.environ.get("MAX_SESSIONS", "6"))

# A session is closed when nobody is watching the stream for this long (seconds).
NO_VIEWER_TIMEOUT = int(os.environ.get("NO_VIEWER_TIMEOUT", "20"))

# A session is closed when the player sends no input for this long (seconds).
IDLE_INPUT_TIMEOUT = int(os.environ.get("IDLE_INPUT_TIMEOUT", "180"))

# Frames per second sent to the browser (games still run at their own FPS).
STREAM_FPS = int(os.environ.get("STREAM_FPS", "60"))

# "jpg" is fast and small, "png" is sharper but heavier.
FRAME_FORMAT = os.environ.get("FRAME_FORMAT", "jpg")

# Comma separated list of allowed origins, or * for all.
# The Python frontend calls this API server-to-server, so * is fine.
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

RUNNER_PATH = os.environ.get("RUNNER_PATH", str(BASE_DIR / "services" / "game_runner.py"))
