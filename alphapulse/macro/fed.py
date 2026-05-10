from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.macro.models import FedWatchProbability, YieldCurve

logger = logging.getLogger(__name__)


async def get_fed_funds_rate(config: AlphaPulseConfig | None = None) -> float | None:
    """Get current effective Federal Funds Rate via Yahoo Finance ^IRX."""
    try:
        ticker = await asyncio.to_thread(lambda: yf.Ticker("^IRX"))
        info = await asyncio.to_thread(lambda: ticker.info)
        return info.get("regularMarketPrice") or info.get("currentPrice")
    except Exception as e:
        logger.warning(f"Failed to fetch fed funds rate: {e}")
        return None


async def get_yield_curve(config: AlphaPulseConfig | None = None) -> YieldCurve | None:
    """Fetch US Treasury yield curve via Yahoo Finance."""
    treasury_symbols = {
        "rate_3m": "^IRX",
        "rate_2y": "2YY=F",
        "rate_5y": "5YY=F",
        "rate_10y": "10YY=F",
        "rate_30y": "30YY=F",
    }
    try:
        symbols = list(treasury_symbols.values())
        tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(symbols)))
        values: dict[str, float | None] = {}
        for key, sym in treasury_symbols.items():
            try:
                t = tickers.tickers.get(sym)
                if t is None:
                    values[key] = None
                    continue
                info = await asyncio.to_thread(lambda x=t: x.info)()
                values[key] = info.get("regularMarketPrice") or info.get("currentPrice")
            except Exception:
                values[key] = None

        r2 = values.get("rate_2y")
        r10 = values.get("rate_10y")
        spread = ((r10 - r2) if (r10 is not None and r2 is not None) else None)

        return YieldCurve(
            rate_3m=values.get("rate_3m"),
            rate_2y=r2,
            rate_5y=values.get("rate_5y"),
            rate_10y=r10,
            rate_30y=values.get("rate_30y"),
            spread_2s10s=round(spread, 4) if spread is not None else None,
        )
    except Exception as e:
        logger.warning(f"Failed to fetch yield curve: {e}")
        return None


async def get_dxy(config: AlphaPulseConfig | None = None) -> float | None:
    """Get US Dollar Index."""
    try:
        ticker = await asyncio.to_thread(lambda: yf.Ticker("DX-Y.NYB"))
        info = await asyncio.to_thread(lambda: ticker.info)
        return info.get("regularMarketPrice") or info.get("currentPrice")
    except Exception as e:
        logger.warning(f"Failed to fetch DXY: {e}")
        return None


async def get_wti_crude(config: AlphaPulseConfig | None = None) -> float | None:
    """Get WTI Crude Oil price."""
    try:
        ticker = await asyncio.to_thread(lambda: yf.Ticker("CL=F"))
        info = await asyncio.to_thread(lambda: ticker.info)
        return info.get("regularMarketPrice") or info.get("currentPrice")
    except Exception as e:
        logger.warning(f"Failed to fetch WTI: {e}")
        return None


async def get_vix(config: AlphaPulseConfig | None = None) -> float | None:
    """Get VIX index value."""
    try:
        ticker = await asyncio.to_thread(lambda: yf.Ticker("^VIX"))
        info = await asyncio.to_thread(lambda: ticker.info)
        return info.get("regularMarketPrice") or info.get("currentPrice")
    except Exception as e:
        logger.warning(f"Failed to fetch VIX: {e}")
        return None
