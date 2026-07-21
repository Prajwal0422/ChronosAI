import pytest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecureP@ss123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        password = "SecureP@ss123"
        hashed = hash_password(password)
        assert verify_password("WrongPassword", hashed) is False

    def test_same_password_different_hashes(self):
        password = "SecureP@ss123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWT:
    def test_create_access_token(self):
        token = create_access_token({"sub": "user123", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_access_token(self):
        token = create_access_token({"sub": "user123", "role": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token({"sub": "user123"})
        payload = decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    def test_expired_token_raises_error(self):
        import time
        from datetime import datetime, timedelta, timezone
        from app.config import settings
        from jose import jwt

        expired_data = {
            "sub": "user123",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(expired_data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_token(token)

    def test_invalid_token_raises_error(self):
        with pytest.raises(ValueError, match="Invalid or expired token"):
            decode_token("invalid_token_here")
