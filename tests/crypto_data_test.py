import pytest
from unittest.mock import AsyncMock, patch
from crypto_data import CryptoManager


@pytest.mark.asyncio
async def test_get_crypto_data():
    manager = CryptoManager()
    mock_response = {
        "name": "Bitcoin",
        "symbol": "btc",
        "market_data": {
            "current_price": {"usd": 50000},
            "market_cap": {"usd": 1000000000000},
            "total_volume": {"usd": 30000000000},
            "price_change_24h_in_currency": {"usd": -500},
            "price_change_percentage_24h": -1.0,
            "price_change_percentage_7d": 5.0,
            "price_change_percentage_30d": 20.0
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        await manager.get_crypto_data("bitcoin")

    assert "bitcoin" in manager.crypto_data
    assert manager.crypto_data["bitcoin"].name == "Bitcoin"
    assert manager.crypto_data["bitcoin"].price == 50000


@pytest.mark.asyncio
async def test_get_global_crypto_data():
    manager = CryptoManager()
    mock_response = {
        "data": {
            "market_cap_percentage": {"BTC": 40.0},
            "total_market_cap": {"usd": 2000000000000}
        }
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        await manager.get_global_crypto_data()

    assert manager.global_crypto_data["data"]["market_cap_percentage"]["BTC"] == 40.0
    assert manager.crypto_total_mcap == 2000000000000


# Example for cg_history_to_postgres
@pytest.mark.asyncio
async def test_cg_history_to_postgres():
    manager = CryptoManager()
    mock_historical_response = {"prices": [[1609459200000, 50000]],
                                 "market_caps": [[1609459200000, 1000000000000]],
                                 "total_volumes": [[1609459200000, 30000000000]]}
    mock_asset_response = {"name": "Bitcoin", "symbol": "BTC"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            AsyncMock(json=AsyncMock(return_value=mock_historical_response)),
            AsyncMock(json=AsyncMock(return_value=mock_asset_response)),
        ]
        await manager.cg_history_to_postgres("bitcoin")
    # Add specific database assertions here
