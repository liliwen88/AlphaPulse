"""Shared pytest fixtures for AlphaPulse tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from alphapulse.core.config import AlphaPulseConfig


@pytest.fixture
def config() -> AlphaPulseConfig:
    return AlphaPulseConfig(cache_ttl_seconds=0)


@pytest.fixture
def sample_ohlcv_df() -> pd.DataFrame:
    """Generate realistic OHLCV data for testing indicators."""
    np.random.seed(42)
    n = 252
    dates = pd.date_range(end="2026-05-10", periods=n, freq="B")
    close = 150 + np.cumsum(np.random.randn(n) * 2)
    close = np.maximum(close, 10)
    high = close + np.abs(np.random.randn(n) * 1.5)
    low = close - np.abs(np.random.randn(n) * 1.5)
    volume = np.random.randint(1_000_000, 10_000_000, n)
    return pd.DataFrame({
        "Open": np.roll(close, 1),
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume,
    }, index=dates)


@pytest.fixture
def mock_yf_ticker():
    """Mock yfinance Ticker with realistic data."""
    with patch("yfinance.Ticker") as mock:
        ticker = MagicMock()
        ticker.info = {
            "symbol": "AAPL",
            "longName": "Apple Inc.",
            "shortName": "Apple",
            "exchange": "NASDAQ",
            "currentPrice": 175.0,
            "regularMarketPrice": 175.0,
            "previousClose": 173.5,
            "volume": 55_000_000,
            "regularMarketVolume": 55_000_000,
            "averageVolume10days": 50_000_000,
            "marketCap": 2_700_000_000_000,
            "trailingPE": 28.5,
            "forwardPE": 26.0,
            "trailingEps": 6.14,
            "fiftyTwoWeekHigh": 200.0,
            "fiftyTwoWeekLow": 150.0,
            "dividendYield": 0.005,
            "beta": 1.25,
            "shortPercentOfFloat": 0.015,
            "currency": "USD",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "fullTimeEmployees": 164000,
            "website": "https://www.apple.com",
            "longBusinessSummary": "Apple Inc. designs, manufactures, and markets smartphones...",
            "returnOnEquity": 1.45,
            "returnOnCapital": 0.35,
            "revenueGrowth": 0.05,
            "sharesOutstanding": 15_500_000_000,
        }
        mock.return_value = ticker
        yield mock
