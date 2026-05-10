from __future__ import annotations

import asyncio
import logging
from typing import Any

import pandas as pd

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.errors import DataUnavailableError
from alphapulse.core.models import DataFreshness, DataSource

logger = logging.getLogger(__name__)


class YahooFinanceProvider:
    """Async wrapper around yfinance for fetching stock data."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()

    async def get_info(self, symbol: str) -> dict[str, Any]:
        symbol = self._validate_symbol(symbol)
        try:
            ticker = await asyncio.to_thread(self._get_ticker, symbol)
            info = await asyncio.to_thread(lambda: ticker.info)
            if not info or info.get("trailingPegRatio") is None and info.get("symbol") is None:
                if not info or info.get("regularMarketPrice") is None:
                    info = await self._retry_fetch(symbol)
            return info
        except Exception as e:
            logger.warning(f"Primary fetch failed for {symbol}: {e}")
            try:
                return await self._retry_fetch(symbol)
            except Exception as e2:
                raise DataUnavailableError(symbol, str(e2)) from e2

    async def get_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> pd.DataFrame:
        symbol = self._validate_symbol(symbol)
        try:
            ticker = await asyncio.to_thread(self._get_ticker, symbol)
            df = await asyncio.to_thread(lambda: ticker.history(period=period, interval=interval))
            if df.empty:
                raise DataUnavailableError(symbol, "No historical data returned")
            return df
        except Exception as e:
            if isinstance(e, DataUnavailableError):
                raise
            raise DataUnavailableError(symbol, str(e)) from e

    async def get_batch_info(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        import yfinance as yf

        symbols = [self._validate_symbol(s) for s in symbols]
        try:
            tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(symbols)))
            result: dict[str, dict[str, Any]] = {}
            for sym, t in tickers.tickers.items():
                try:
                    info = await asyncio.to_thread(lambda: dict(t.info)) if t and hasattr(t, 'info') else {}
                    result[sym] = info if info else {}
                except Exception:
                    result[sym] = {}
            return result
        except Exception as e:
            logger.warning(f"Batch fetch failed: {e}")
            results = await asyncio.gather(
                *[self.get_info(s) for s in symbols],
                return_exceptions=True,
            )
            result = {}
            for sym, r in zip(symbols, results):
                if isinstance(r, Exception):
                    logger.warning(f"Failed to fetch {sym}: {r}")
                    result[sym] = {}
                else:
                    result[sym] = r
            return result

    @staticmethod
    def _get_ticker(symbol: str):
        import yfinance as yf
        return yf.Ticker(symbol)

    @staticmethod
    def _validate_symbol(symbol: str) -> str:
        return symbol.strip().upper()

    @staticmethod
    async def _retry_fetch(symbol: str) -> dict[str, Any]:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = await asyncio.to_thread(lambda: ticker.info)
        if not info:
            raise DataUnavailableError(symbol, "Empty response from Yahoo Finance")
        return info

    @staticmethod
    def freshness() -> DataFreshness:
        return DataFreshness(source=DataSource.YAHOO_FINANCE)
