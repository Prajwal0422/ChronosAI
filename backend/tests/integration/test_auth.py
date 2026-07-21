import pytest


@pytest.mark.asyncio
class TestAuth:
    async def test_login_missing_fields(self, client):
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    async def test_login_invalid_credentials(self, client):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.edu",
            "password": "wrong",
        })
        assert response.status_code in (401, 422, 400)

    async def test_register_creates_user(self, client, db_session):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@test.edu",
            "password": "SecurePass123!",
            "full_name": "New User",
        })
        assert response.status_code in (201, 200)
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@test.edu"

    async def test_register_duplicate_email(self, client, db_session):
        await client.post("/api/v1/auth/register", json={
            "email": "dup@test.edu",
            "password": "SecurePass123!",
            "full_name": "User One",
        })
        response = await client.post("/api/v1/auth/register", json={
            "email": "dup@test.edu",
            "password": "SecurePass456!",
            "full_name": "User Two",
        })
        assert response.status_code in (409, 400)

    async def test_auth_me_requires_token(self, client):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_auth_me_with_valid_token(self, auth_client):
        response = await auth_client.get("/api/v1/auth/me")
        assert response.status_code in (200, 404)
        if response.status_code == 200:
            data = response.json()
            assert "email" in data
