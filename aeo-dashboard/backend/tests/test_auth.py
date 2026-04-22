"""Password hashing + token round-trip."""
from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip() -> None:
    h = hash_password("hunter2")
    assert h != "hunter2"
    assert verify_password("hunter2", h) is True
    assert verify_password("wrong", h) is False


def test_jwt_roundtrip() -> None:
    token = create_access_token(42, extra={"org": 7, "role": "admin"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["org"] == 7
    assert payload["role"] == "admin"


def test_invalid_token_returns_none() -> None:
    assert decode_token("garbage") is None
