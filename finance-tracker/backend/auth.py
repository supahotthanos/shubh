"""Single-password session auth.

- Password defaults to ``Shubh2007$``; override with ``FINANCE_PASSWORD`` env var.
- Server signs a session token (HMAC-SHA256 over a 30-day expiry timestamp) using a
  secret persisted at ``data/secret.key``. The secret is generated on first run.
- Token is delivered via an HttpOnly cookie. ``require_auth`` is a FastAPI dependency
  that 401s if the cookie is missing/invalid/expired.
"""

from __future__ import annotations

import hmac
import os
import secrets
import time
from hashlib import sha256
from pathlib import Path

from fastapi import Cookie, HTTPException, Response

PASSWORD = os.environ.get("FINANCE_PASSWORD", "Shubh2007$")
COOKIE_NAME = "ft_session"
SESSION_TTL = 60 * 60 * 24 * 30  # 30 days
SECRET_PATH = Path(__file__).resolve().parent.parent / "data" / "secret.key"


def _load_or_create_secret() -> bytes:
    SECRET_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SECRET_PATH.exists():
        return SECRET_PATH.read_bytes()
    secret = secrets.token_bytes(32)
    SECRET_PATH.write_bytes(secret)
    try:
        os.chmod(SECRET_PATH, 0o600)
    except OSError:
        pass
    return secret


_SECRET = _load_or_create_secret()


def _sign(payload: str) -> str:
    return hmac.new(_SECRET, payload.encode(), sha256).hexdigest()


def make_token(now: int | None = None) -> str:
    exp = (now or int(time.time())) + SESSION_TTL
    payload = str(exp)
    return f"{payload}.{_sign(payload)}"


def verify_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    payload, sig = token.rsplit(".", 1)
    expected = _sign(payload)
    if not hmac.compare_digest(sig, expected):
        return False
    try:
        exp = int(payload)
    except ValueError:
        return False
    return exp > int(time.time())


def check_password(submitted: str) -> bool:
    return hmac.compare_digest(submitted.encode(), PASSWORD.encode())


def set_session_cookie(response: Response) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=make_token(),
        httponly=True,
        samesite="lax",
        max_age=SESSION_TTL,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def require_auth(ft_session: str | None = Cookie(default=None)) -> None:
    if not verify_token(ft_session):
        raise HTTPException(status_code=401, detail="Not authenticated")
