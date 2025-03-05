import pytest
from validators import CryptoData, StockData, UserData
from pydantic import ValidationError


def test_crypto_data_validation():
    valid_data = {
        "name": "Bitcoin",
        "ticker": "BTC",
        "price": 50000,
        "mcap": 1000000000000,
        "volume": 50000000000,
        "change_usd_24h": 1000,
        "change_percent_24h": 2.5,
        "change_percent_7d": 5.0,
        "change_percent_30d": 10.0
    }
    crypto_data = CryptoData(**valid_data)
    assert crypto_data.name == "Bitcoin"
    assert crypto_data.ticker == "BTC"
    assert crypto_data.price == 50000
    assert crypto_data.mcap == 1000000000000
    assert crypto_data.volume == 50000000000
    assert crypto_data.change_usd_24h == 1000
    assert crypto_data.change_percent_24h == 2.5
    assert crypto_data.change_percent_7d == 5.0
    assert crypto_data.change_percent_30d == 10.0


def test_stock_data_validation():
    valid_data = {
        "name": "S&P 500",
        "ticker": "SPX",
        "close": 4000,
        "mcap": None,
        "volume": 1000000,
        "change_value_24h": 50,
        "change_percent_24h": 1.25,
        "change_value_weekly": 100,
        "change_percent_weekly": 2.5,
        "change_value_monthly": 200,
        "change_percent_monthly": 5.0
    }
    stock_data = StockData(**valid_data)
    assert stock_data.name == "S&P 500"
    assert stock_data.ticker == "SPX"
    assert stock_data.close == 4000
    assert stock_data.mcap is None
    assert stock_data.volume == 1000000
    assert stock_data.change_value_24h == 50
    assert stock_data.change_percent_24h == 1.25
    assert stock_data.change_value_weekly == 100
    assert stock_data.change_percent_weekly == 2.5
    assert stock_data.change_value_monthly == 200
    assert stock_data.change_percent_monthly == 5.0


def test_user_data_validation():
    valid_data = {"email": "user@email.com"}
    user_data = UserData(**valid_data)
    assert user_data.email == "user@email.com"

    with pytest.raises(ValidationError):
        UserData(email="invalid_email")