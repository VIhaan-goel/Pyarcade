"""Frontend settings (environment variables)."""
import os

# Where the Flask API is, as seen by THIS Python server.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")
PUBLIC_BACKEND_URL = os.environ.get("PUBLIC_BACKEND_URL", BACKEND_URL).rstrip("/")

PORT = int(os.environ.get("PORT", "8080"))
STORAGE_SECRET = os.environ.get("STORAGE_SECRET", "dev-only-change-me")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyarcade.db"))