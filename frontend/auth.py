"""Accounts: SQLite storage, password hashing and "who is logged in". Standard library only."""
import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone

from nicegui import app

from config import DB_PATH

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PBKDF2_ROUNDS = 600_000


class AuthError(Exception):
    """A problem the user can fix (shown on the form)."""


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(_connect()) as conn, conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                   id            TEXT PRIMARY KEY,
                   username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
                   email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
                   password_hash TEXT NOT NULL,
                   created_at    TEXT NOT NULL
               )"""
        )


def _hash_password(password, salt=None, rounds=PBKDF2_ROUNDS):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}"


def _verify_password(password, stored):
    try:
        _, rounds, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds))
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


_DUMMY_HASH = _hash_password("not-a-real-password")  # keeps login time the same for unknown users


def create_user(username, email, password):
    """Validate, store and return the new user's unique id. Raises AuthError on bad input."""
    username = (username or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    if not USERNAME_RE.match(username):
        raise AuthError("Username must be 3-20 characters: letters, numbers or underscore.")
    if not EMAIL_RE.match(email):
        raise AuthError("Enter a valid email address.")
    if not 8 <= len(password) <= 128:
        raise AuthError("Password must be 8 to 128 characters.")

    user_id = str(uuid.uuid4())  # the unique ID of this player
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with closing(_connect()) as conn, conn:
            conn.execute(
                "INSERT INTO users (id, username, email, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, email, _hash_password(password), created),
            )
    except sqlite3.IntegrityError:
        raise AuthError("That username or email is already taken.") from None
    return user_id


def authenticate(identifier, password):
    """Return the user's id if the username/email and password match, otherwise None."""
    identifier = (identifier or "").strip()
    password = (password or "")[:128]
    if not identifier:
        return None
    with closing(_connect()) as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE username = ? OR email = ?", (identifier, identifier)
        ).fetchone()
    if row is None:
        _verify_password(password, _DUMMY_HASH)
        return None
    return row["id"] if _verify_password(password, row["password_hash"]) else None


def current_user():
    """The logged-in user as a dict (id, username, email, created_at), or None."""
    user_id = app.storage.user.get("user_id")
    if not user_id:
        return None
    with closing(_connect()) as conn:
        row = conn.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:  # account no longer exists
        app.storage.user.pop("user_id", None)
        return None
    return dict(row)


def short_id(user_id):
    """Friendly form of the id for display, e.g. EE6A11CB."""
    return user_id.replace("-", "")[:8].upper()


init_db()