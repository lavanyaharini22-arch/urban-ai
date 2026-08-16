"""
Password hashing and lightweight session-token authentication.
Passwords are never stored in plain text.
"""
import re
import secrets
import time
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory session store: token -> {email, expires_at}
# Simple and sufficient for a single-instance demo/final-year project.
_SESSIONS = {}
SESSION_TTL_SECONDS = 60 * 60 * 8  # 8 hours

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify(password, password_hash)
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email or ""))


def is_strong_password(password: str) -> tuple[bool, str]:
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""


def create_session(email: str) -> str:
    token = secrets.token_hex(32)
    _SESSIONS[token] = {"email": email, "expires_at": time.time() + SESSION_TTL_SECONDS}
    return token


def get_session_email(token: str):
    session = _SESSIONS.get(token)
    if not session:
        return None
    if session["expires_at"] < time.time():
        _SESSIONS.pop(token, None)
        return None
    return session["email"]


def destroy_session(token: str):
    _SESSIONS.pop(token, None)
