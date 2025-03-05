import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select
from models import Asset, AssetData, Base
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import pytest_asyncio
import pytest
from utils import (up_down_icon, default_msg, htf_msg, format_coingecko_ids, format_percent, format_dollars,
                   save_data_to_postgres)

# Database and Session setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


# Pytest Fixture for setting up and tearing down the database
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
async def test_save_data_to_postgres(test_db):
    async with test_db as async_session:
        # Test adding a new asset
        await save_data_to_postgres("Bitcoin", "BTC", 50000, 1000000000000, 30000000000, session=async_session)

        # Query the asset and asset data
        asset = await async_session.scalar(select(Asset).filter_by(asset_name="Bitcoin"))
        assert asset.asset_name == "Bitcoin"
        assert asset.asset_ticker == "BTC"

        asset_data = await async_session.scalar(select(AssetData).filter_by(asset_id=asset.asset_id))
        assert asset_data.close_price == 50000
        assert asset_data.market_cap == 1000000000000
        assert asset_data.volume_USD == 30000000000


def test_up_down_icon():
    assert up_down_icon(0.1) == "🟢"
    assert up_down_icon(-0.1) == "🔴"
    assert up_down_icon(0.000) == ""


def test_format_dollars():
    assert format_dollars(1) == "$1.00"
    assert format_dollars(0) == "$0.00000000"
    assert format_dollars(-1) == "-$1.00"
    assert format_dollars(0.02) == "$0.0200"
    assert format_dollars(0.002) == "$0.00200000"


def test_format_percent():
    assert format_percent(1) == "1.00%"
    assert format_percent(-1) == "-1.00%"
    assert format_percent(1.13) == "1.13%"
    assert format_percent(1.1) == "1.10%"


def test_default_msg():
    result1 = default_msg(ticker="BTC",
                          price=40000,
                          percent_change=0.5)
    assert result1 == "BTC: $40,000.00 🟢 0.50%<br>"

    result2 = default_msg(ticker="ETH",
                          price=3000,
                          percent_change=1)
    assert result2 == "ETH: $3,000.00 🟢 1.00%<br>"

    result3 = default_msg(ticker="DOGE",
                          price=0.3012,
                          percent_change=3.644)
    assert result3 == "DOGE: $0.3012 🟢 3.64%<br>"

    result4 = default_msg(ticker="SOL",
                          price=217.6632,
                          percent_change=-1.645)
    assert result4 == "SOL: $217.66 🔴 -1.65%<br>"


def test_htf_msg():
    result1 = htf_msg(timeframe="7D",
                      percent_change=0.87
                      )
    assert result1 == "&nbsp;&nbsp;7D 🟢 0.87%<br>"

    result2 = htf_msg(timeframe="1M",
                      percent_change=1
                      )
    assert result2 == "&nbsp;&nbsp;1M 🟢 1.00%<br>"

    result3 = htf_msg(timeframe="7D",
                      percent_change=-1.1
                      )
    assert result3 == "&nbsp;&nbsp;7D 🔴 -1.10%<br>"


def test_format_coingecko_ids():
    result1 = format_coingecko_ids("Ethereum (ETH), Solana (SOL), Dogecoin (DOGE), Bittensor (TAO), DogWifHat "
                                   "(WIF), Mother Iggy (MOTHER), Ondo (ONDO), Pepe (PEPE), Toncoin (TON)")
    assert result1 == ['Ethereum', '(ETH),', 'Solana', '(SOL),', 'Dogecoin', '(DOGE),', 'Bittensor',
                       '(TAO),', 'dogwifcoin', '(WIF),', 'mother-iggy', '(MOTHER),', 'ondo-finance',
                       '(ONDO),', 'Pepe', '(PEPE),', 'the-open-network', '(TON)']
    result2 = format_coingecko_ids("Ethereum (ETH), Solana (SOL), Dogecoin (DOGE)")
    assert result2 == ["Ethereum", "(ETH),", "Solana", "(SOL),", "Dogecoin", "(DOGE)"]
    result3 = format_coingecko_ids(None)
    assert result3 == []
    result4 = format_coingecko_ids("")
    assert result4 == []
