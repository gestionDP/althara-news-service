"""Basic API tests."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client():
    """AsyncClient runs in same event loop as app, avoiding 'Future attached to different loop'."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


async def test_health(async_client: AsyncClient):
    r = await async_client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_list_news_domain_filter(async_client: AsyncClient):
    r = await async_client.get("/api/news?domain=tech&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    for item in data["items"]:
        assert item.get("domain") == "tech"


async def test_list_news_real_estate(async_client: AsyncClient):
    r = await async_client.get("/api/news?domain=real_estate&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
