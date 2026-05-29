"""Fetch real-time market data from yfinance."""

from __future__ import annotations

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os

# Disable yfinance cache to fix database issues
os.environ["YFINANCE_CACHE_ENABLED"] = "False"
os.environ["YFINANCE_CACHE_DIR"] = ""
os.environ["YFINANCE_NO_CACHE"] = "1"

sys.path.insert(0, str(Path(__file__).parent))

# Try to patch yfinance cache before importing
try:
    import yfinance.cache
    if hasattr(yfinance.cache, 'Cache'):
        yfinance.cache.Cache.initialise = lambda self: None
except (ImportError, AttributeError):
    pass

import yfinance as yf
import pandas as pd
from models import MarketSnapshot
from config import (
    DEFAULT_PERIOD,
    SUPPORT_RESISTANCE_LOOKBACK,
    SUPPORT_RESISTANCE_THRESHOLD,
    YFINANCE_TIMEOUT,
)

KNOWN_MARKET_SUFFIXES = {".HK", ".T", ".L", ".SI", ".DE", ".F", ".PA", ".MC", ".AS", ".SW"}


def resolve_ticker(ticker: str) -> str:
    """Normalize ticker for yfinance. Pass-through if suffix already present."""
    upper = ticker.upper()
    for suffix in KNOWN_MARKET_SUFFIXES:
        if upper.endswith(suffix):
            return upper
    return upper


def detect_market(ticker: str) -> str:
    """Return market label for macro classification."""
    upper = ticker.upper()
    if upper.endswith(".HK"):
        return "hk"
    if upper.endswith(".T"):
        return "jp"
    if upper.endswith(".SI"):
        return "sg"
    if upper.endswith(".L"):
        return "uk"
    if any(upper.endswith(s) for s in [".DE", ".F", ".PA", ".MC", ".AS", ".SW"]):
        return "eu"
    return "us"


def calculate_support_resistance(history: pd.DataFrame) -> tuple[float | None, float | None]:
    """Find local minima (support) and maxima (resistance) from recent price history."""
    if history.empty or len(history) < SUPPORT_RESISTANCE_LOOKBACK:
        return None, None

    recent = history.tail(SUPPORT_RESISTANCE_LOOKBACK * 2)
    lows = recent["Low"].values
    highs = recent["High"].values
    window = SUPPORT_RESISTANCE_LOOKBACK // 4 or 3

    local_minima = []
    local_maxima = []
    for i in range(window, len(lows) - window):
        if all(lows[i] <= lows[i - j] for j in range(1, window + 1)) and all(
            lows[i] <= lows[i + j] for j in range(1, window + 1)
        ):
            local_minima.append(lows[i])
        if all(highs[i] >= highs[i - j] for j in range(1, window + 1)) and all(
            highs[i] >= highs[i + j] for j in range(1, window + 1)
        ):
            local_maxima.append(highs[i])

    support = float(min(local_minima)) if local_minima else None
    resistance = float(max(local_maxima)) if local_maxima else None
    return support, resistance


def compute_momentum(history: pd.DataFrame) -> dict[str, float]:
    """Calculate percentage change over 1d, 1w, 1m, 3m."""
    if history.empty or len(history) < 2:
        return {"1d": 0.0, "1w": 0.0, "1m": 0.0, "3m": 0.0}

    closes = history["Close"]
    latest = float(closes.iloc[-1])

    def pct_change_from(lookback: int) -> float:
        if len(closes) <= lookback:
            return 0.0
        prev = float(closes.iloc[-(lookback + 1)])
        return round((latest - prev) / prev * 100, 2) if prev != 0 else 0.0

    return {
        "1d": pct_change_from(1),
        "1w": pct_change_from(5),
        "1m": pct_change_from(21),
        "3m": pct_change_from(63),
    }


class MarketDataError(Exception):
    """Raised when market data cannot be fetched."""


def fetch_market_data(ticker: str) -> MarketSnapshot:
    """Fetch all market data from yfinance and return a structured MarketSnapshot."""
    resolved = resolve_ticker(ticker)
    stock = yf.Ticker(resolved)

    history = stock.history(period=DEFAULT_PERIOD, timeout=YFINANCE_TIMEOUT)
    info = dict(stock.info) if stock.info else {}

    if history.empty and not info:
        raise MarketDataError(f"No data returned for {resolved} — Yahoo Finance may be rate limiting or unavailable")

    now = datetime.now(timezone.utc)

    if not history.empty:
        latest_row = history.iloc[-1]
        current_price = float(latest_row["Close"])
        prev_close = float(info.get("previousClose", history.iloc[-2]["Close"] if len(history) > 1 else current_price))
        day_change_pct = round((current_price - prev_close) / prev_close * 100, 2) if prev_close != 0 else 0.0
        volume = int(latest_row.get("Volume", 0))
        avg_vol_series = history["Volume"].rolling(20).mean()
        avg_volume = int(avg_vol_series.iloc[-1]) if not avg_vol_series.empty and pd.notna(avg_vol_series.iloc[-1]) else volume
        volume_ratio = round(volume / avg_volume, 2) if avg_volume > 0 else 1.0

        high_52w = float(info.get("fiftyTwoWeekHigh", history["High"].max()))
        low_52w = float(info.get("fiftyTwoWeekLow", history["Low"].min()))
        range_52w = high_52w - low_52w
        position_52w = round((current_price - low_52w) / range_52w * 100, 1) if range_52w > 0 else 50.0

        support, resistance = calculate_support_resistance(history)
        momentum = compute_momentum(history)
    else:
        current_price = float(info.get("currentPrice", info.get("regularMarketPrice", 0)))
        prev_close = float(info.get("previousClose", current_price))
        day_change_pct = round((current_price - prev_close) / prev_close * 100, 2) if prev_close != 0 else 0.0
        volume = int(info.get("volume", 0))
        avg_volume = int(info.get("averageVolume", volume))
        volume_ratio = round(volume / avg_volume, 2) if avg_volume > 0 else 1.0
        high_52w = float(info.get("fiftyTwoWeekHigh", 0))
        low_52w = float(info.get("fiftyTwoWeekLow", 0))
        range_52w = high_52w - low_52w
        position_52w = round((current_price - low_52w) / range_52w * 100, 1) if range_52w > 0 else 50.0
        support, resistance = None, None
        momentum = {"1d": 0.0, "1w": 0.0, "1m": 0.0, "3m": 0.0}

    market_cap = info.get("marketCap")
    pe_ratio = info.get("trailingPE")
    dividend_yield = info.get("dividendYield")
    if dividend_yield is not None:
        dividend_yield = round(dividend_yield * 100, 2)

    return MarketSnapshot(
        ticker=resolved,
        timestamp=now,
        current_price=current_price,
        previous_close=prev_close,
        day_change_pct=day_change_pct,
        volume=volume,
        avg_volume=avg_volume,
        volume_ratio=volume_ratio,
        market_cap=market_cap,
        pe_ratio=pe_ratio,
        dividend_yield=dividend_yield,
        fifty_two_week_high=high_52w,
        fifty_two_week_low=low_52w,
        fifty_two_week_position_pct=position_52w,
        support_level=support,
        resistance_level=resistance,
        momentum=momentum,
        data_source="yfinance",
        data_freshness=f"Price data: {now.strftime('%Y-%m-%d %H:%M UTC')}",
    )


def main():
    parser = argparse.ArgumentParser(description="Fetch real-time market data for a ticker")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, 0700.HK)")
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    try:
        snapshot = fetch_market_data(args.ticker)
    except Exception as e:
        print(f"Error fetching market data for {args.ticker}: {e}", file=sys.stderr)
        sys.exit(1)

    json_str = json.dumps(snapshot.model_dump(), indent=2, default=str, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"Market data saved to {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
