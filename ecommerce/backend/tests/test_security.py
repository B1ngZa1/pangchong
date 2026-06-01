"""
Tests for security module: password hashing, JWT tokens, password strength validation.
"""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_tokens,
    verify_token,
    validate_password_strength,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "SecurePass1"
        hashed = get_password_hash(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("Correct1")
        assert not verify_password("Wrong1", hashed)

    def test_hash_is_deterministic_per_call(self):
        """Each call produces different salt."""
        h1 = get_password_hash("Test123")
        h2 = get_password_hash("Test123")
        assert h1 != h2  # bcrypt random salt


class TestJWT:
    def test_create_and_verify_access_token(self):
        tokens = create_tokens("user-uuid-123")
        payload = verify_token(tokens["access_token"])
        assert payload is not None
        assert payload["sub"] == "user-uuid-123"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_and_verify_refresh_token(self):
        tokens = create_tokens("user-uuid-456")
        payload = verify_token(tokens["refresh_token"], "refresh")
        assert payload is not None
        assert payload["sub"] == "user-uuid-456"
        assert payload["type"] == "refresh"

    def test_verify_with_wrong_type_fails(self):
        tokens = create_tokens("user-uuid")
        payload = verify_token(tokens["access_token"], "refresh")
        assert payload is None

    def test_verify_invalid_token(self):
        assert verify_token("invalid.token.here") is None
        assert verify_token("") is None

    def test_token_response_structure(self):
        tokens = create_tokens("test-id")
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert len(tokens["access_token"]) > 20
        assert len(tokens["refresh_token"]) > 20


class TestPasswordStrength:
    def test_valid_password(self):
        ok, msg = validate_password_strength("Testpass1")
        assert ok
        assert msg == ""

    def test_too_short(self):
        ok, msg = validate_password_strength("Ab1")
        assert not ok
        assert "长度" in msg

    def test_no_uppercase(self):
        ok, msg = validate_password_strength("testpass1")
        assert not ok
        assert "大写" in msg

    def test_no_digit(self):
        ok, msg = validate_password_strength("TestpassWord")
        assert not ok
        assert "数字" in msg

    def test_unicode_password(self):
        ok, msg = validate_password_strength("密码Test1Long")
        assert ok
