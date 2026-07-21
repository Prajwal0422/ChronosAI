import pytest


@pytest.mark.asyncio
class TestHealth:
    async def test_health_endpoint(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    async def test_api_root_redirect(self, client):
        response = await client.get("/api/v1/")
        assert response.status_code in (200, 404)
