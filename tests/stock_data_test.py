import pytest
from unittest.mock import AsyncMock, patch
from stock_data import StockManager


@pytest.mark.asyncio
async def test_get_index_data():
    manager = StockManager()
    mock_response = {
        "data": [{
            "d": ["SPX", 4500, 35000000000, 200000000, -50, -1.1, -100, -2.2, -200, -4.4]
        }]
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.raise_for_status = AsyncMock()
        await manager.get_index_data("SP:SPX")

    assert manager.index_data["SPX"].name == "SPX"
    assert manager.index_data["SPX"].close == 4500
    assert manager.index_data["SPX"].change_percent_24h == -1.1
