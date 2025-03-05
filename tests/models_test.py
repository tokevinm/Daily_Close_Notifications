import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from models import Base, Asset, AssetData, User

# Database and Session setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide the session to the test
    async with TestSession() as session:
        yield session

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_asset_creation(test_db):
    async with test_db as async_session:
        asset = Asset(asset_name="Bitcoin", asset_ticker="BTC")
        async_session.add(asset)
        await async_session.commit()

        result = await async_session.get(Asset, asset.asset_id)
        assert result.asset_name == "Bitcoin"
        assert result.asset_ticker == "BTC"


@pytest.mark.asyncio
async def test_asset_data_creation(test_db):
    async with test_db as async_session:
        asset = Asset(asset_name="Ethereum", asset_ticker="ETH")
        async_session.add(asset)
        await async_session.commit()

        asset_data = AssetData(asset_id=asset.asset_id, close_price=2000.00, volume_USD=1000000)
        async_session.add(asset_data)
        await async_session.commit()

        result = await async_session.get(AssetData, asset_data.data_id)
        assert result.close_price == 2000.00
        assert result.volume_USD == 1000000


@pytest.mark.asyncio
async def test_user_creation(test_db):
    async with test_db as async_session:
        user = User(email="user@email.com", unsubscribe=True)
        async_session.add(user)
        await async_session.commit()

        result = await async_session.get(User, user.user_id)
        assert result.email == "user@email.com"
        assert result.unsubscribe
        assert result.unsubscribe is not False
