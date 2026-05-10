from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.hotspots.models import SectorPerformance, TopMover

logger = logging.getLogger(__name__)

_SECTOR_ETFS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Communication Services": "XLC",
}

_watchlist_cache: list[str] | None = None


def _get_watchlist() -> list[str]:
    """A curated watchlist of liquid US large-cap stocks for screening."""
    global _watchlist_cache
    if _watchlist_cache is None:
        _watchlist_cache = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "UNH",
            "JNJ", "V", "PG", "JPM", "MA", "HD", "DIS", "BAC", "NFLX", "ADBE",
            "CRM", "AMD", "INTC", "QCOM", "TXN", "PFE", "BA", "CAT", "GE",
            "GM", "F", "UBER", "LYFT", "SNAP", "PINS", "SQ", "PYPL", "COIN",
            "MARA", "RIOT", "GME", "AMC", "PLTR", "SNOW", "DDOG", "CRWD",
            "ZM", "ROKU", "SHOP", "SPOT", "ABNB", "NKE", "SBUX", "COST",
            "WMT", "TGT", "ORCL", "CSCO", "IBM", "CVX", "XOM", "COP",
            "OXY", "DVN", "SLB", "FCX", "NEM", "GOLD", "GS", "MS",
            "C", "WFC", "BLK", "SCHW", "LMT", "RTX", "NOC",
        ]
    return _watchlist_cache


async def get_sector_performance(config: AlphaPulseConfig | None = None) -> list[SectorPerformance]:
    symbols = list(_SECTOR_ETFS.values())
    try:
        tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(symbols)))
        results = []
        for sector, sym in _SECTOR_ETFS.items():
            try:
                t = tickers.tickers.get(sym)
                if t is None:
                    continue
                info = await asyncio.to_thread(lambda x=t: x.info)()
                current = info.get("regularMarketPrice") or info.get("currentPrice") or 0.0
                prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
                day_change = ((current - prev) / prev * 100) if prev != 0 else 0.0

                rot_signal = None
                if day_change > 1.0:
                    rot_signal = "strengthening"
                elif day_change < -1.0:
                    rot_signal = "weakening"

                results.append(SectorPerformance(
                    sector=sector,
                    etf_symbol=sym,
                    change_pct_day=round(day_change, 2),
                    rotation_signal=rot_signal,
                ))
            except Exception as e:
                logger.warning(f"Failed to fetch sector {sector}: {e}")
        results.sort(key=lambda x: x.change_pct_day, reverse=True)
        return results
    except Exception as e:
        logger.warning(f"Batch sector fetch failed: {e}")
        return []


async def get_top_movers(
    n: int = 10,
    config: AlphaPulseConfig | None = None,
) -> tuple[list[TopMover], list[TopMover]]:
    watchlist = _get_watchlist()
    try:
        tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(watchlist)))
        movers = []
        for sym in watchlist:
            try:
                t = tickers.tickers.get(sym)
                if t is None:
                    continue
                info = await asyncio.to_thread(lambda x=t: x.info)()
                current = info.get("regularMarketPrice") or info.get("currentPrice") or 0.0
                prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
                change_pct = ((current - prev) / prev * 100) if prev != 0 else 0.0
                volume = info.get("volume") or info.get("regularMarketVolume") or 0
                avg_vol = info.get("averageVolume") or info.get("averageDailyVolume10Day") or 1
                movers.append(TopMover(
                    symbol=sym,
                    company_name=info.get("shortName") or info.get("longName") or sym,
                    price=round(current, 2),
                    change_pct=round(change_pct, 2),
                    volume=volume,
                    volume_vs_avg_pct=round(volume / avg_vol * 100, 1) if avg_vol > 0 else None,
                ))
            except Exception:
                continue
        movers.sort(key=lambda x: x.change_pct, reverse=True)
        gainers = [m for m in movers if m.change_pct > 0][:n]
        losers = [m for m in movers if m.change_pct < 0][::-1][:n]
        return gainers, losers
    except Exception as e:
        logger.warning(f"Failed to get top movers: {e}")
        return [], []


async def get_unusual_volume(
    n: int = 10,
    threshold: float = 2.0,
    config: AlphaPulseConfig | None = None,
) -> list[TopMover]:
    watchlist = _get_watchlist()
    try:
        tickers = await asyncio.to_thread(lambda: yf.Tickers(" ".join(watchlist)))
        unusual = []
        for sym in watchlist:
            try:
                t = tickers.tickers.get(sym)
                if t is None:
                    continue
                info = await asyncio.to_thread(lambda x=t: x.info)()
                volume = info.get("volume") or info.get("regularMarketVolume") or 0
                avg_vol = info.get("averageVolume") or info.get("averageDailyVolume10Day") or 1
                ratio = volume / avg_vol if avg_vol > 0 else 0
                if ratio >= threshold:
                    current = info.get("regularMarketPrice") or info.get("currentPrice") or 0.0
                    prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
                    change_pct = ((current - prev) / prev * 100) if prev != 0 else 0.0
                    unusual.append(TopMover(
                        symbol=sym,
                        company_name=info.get("shortName") or info.get("longName") or sym,
                        price=round(current, 2),
                        change_pct=round(change_pct, 2),
                        volume=volume,
                        volume_vs_avg_pct=round(ratio * 100, 1),
                    ))
            except Exception:
                continue
        unusual.sort(key=lambda x: x.volume_vs_avg_pct or 0, reverse=True)
        return unusual[:n]
    except Exception as e:
        logger.warning(f"Failed to get unusual volume: {e}")
        return []
