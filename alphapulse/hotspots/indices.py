from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.hotspots.models import MarketIndexSnapshot

logger = logging.getLogger(__name__)

_MAJOR_INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq Composite",
    "^DJI": "Dow Jones Industrial",
    "^RUT": "Russell 2000",
    "^VIX": "CBOE Volatility Index",
}


async def get_major_indices(config: AlphaPulseConfig | None = None) -> list[MarketIndexSnapshot]:
    symbols = list(_MAJOR_INDICES.keys())
    try:
        tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(symbols)))
        results = []
        for sym in symbols:
            try:
                t = tickers.tickers.get(sym)
                if t is None:
                    continue
                info = await asyncio.to_thread(lambda x=t: getattr(x, 'info', {}))()
                info = info() if callable(info) else info
                if not info:
                    info = {}
                current = info.get("regularMarketPrice") or info.get("currentPrice") or 0.0
                prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
                change_pct = ((current - prev) / prev * 100) if prev != 0 else 0.0
                results.append(MarketIndexSnapshot(
                    symbol=sym,
                    name=_MAJOR_INDICES[sym],
                    price=round(current, 2),
                    change_pct=round(change_pct, 2),
                ))
            except Exception as e:
                logger.warning(f"Failed to fetch index {sym}: {e}")
        return results
    except Exception as e:
        logger.warning(f"Batch index fetch failed: {e}, trying sequential")
        return await _fetch_sequential(symbols)


async def _fetch_sequential(symbols: list[str]) -> list[MarketIndexSnapshot]:
    results = []
    for sym in symbols:
        try:
            t = await asyncio.to_thread(lambda s=sym: yf.Ticker(s))
            info = await asyncio.to_thread(lambda x=t: x.info)()
            current = info.get("regularMarketPrice") or info.get("currentPrice") or 0.0
            prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
            change_pct = ((current - prev) / prev * 100) if prev != 0 else 0.0
            results.append(MarketIndexSnapshot(
                symbol=sym,
                name=_MAJOR_INDICES.get(sym, sym),
                price=round(current, 2),
                change_pct=round(change_pct, 2),
            ))
        except Exception as e:
            logger.warning(f"Failed to fetch index {sym}: {e}")
    return results
