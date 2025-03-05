from datetime import datetime
import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from models import Base, Asset, AssetData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from config import AsyncSessionDepends

from fastapi.testclient import TestClient

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_home():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_sign_up():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/signup", data={"email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "'test@example.com' has been signed up for Daily Close Notifications"


@pytest.mark.asyncio
async def test_get_data_on_date(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[AsyncSessionDepends] = override_get_db

    # Add test data to the database
    test_asset = Asset(asset_name="Bitcoin", asset_ticker="BTC")
    test_asset_data = AssetData(
        asset=test_asset,
        date=datetime(2023, 1, 1).date(),
        close_price=50000,
        market_cap=1000000000000,
        volume_USD=30000000000
    )
    test_db.add(test_asset)
    test_db.add(test_asset_data)
    await test_db.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/data/BTC/2023-01-01")

    assert response.status_code == 200
    assert response.json() == {
        "date": "2023-01-01",
        "name": "Bitcoin",
        "ticker": "BTC",
        "price": 50000,
        "volume": 30000000000,
        "market_cap": 1000000000000
    }

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_compare_date_data(test_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/compare/BTC/2023-01-01/2023-01-02")
    assert response.status_code == 200
    assert "change_in_price" in response.json()
    assert "percentage_change" in response.json()
