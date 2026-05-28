"""Calculate technical indicators: RSI, MACD, Bollinger Bands, SMA."""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yfinance as yf
import pandas as pd
import numpy as np
from models import IndicatorSet
from config import (
    DEFAULT_RSI_PERIOD,
    DEFAULT_MACD_FAST,
    DEFAULT_MACD_SLOW,
    DEFAULT_MACD_SIGNAL,
    DEFAULT_BOLLINGER_PERIOD,
    DEFAULT_BOLLINGER_STD,
    DEFAULT_SMA_PERIODS,
    DEFAULT_INDICATORS,
    DEFAULT_PERIOD,
    YFINANCE_TIMEOUT,
)


def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """Get historical OHLCV data from yfinance."""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, timeout=YFINANCE_TIMEOUT)


def calculate_rsi(prices: pd.Series, period: int = DEFAULT_RSI_PERIOD) -> pd.Series:
    """Wilder's smoothed RSI."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast: int = DEFAULT_MACD_FAST,
    slow: int = DEFAULT_MACD_SLOW,
    signal: int = DEFAULT_MACD_SIGNAL,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (macd_line, signal_line, histogram)."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = DEFAULT_BOLLINGER_PERIOD,
    num_std: float = DEFAULT_BOLLINGER_STD,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (upper, middle, lower)."""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def calculate_sma(prices: pd.Series, period: int) -> pd.Series:
    """Simple moving average."""
    return prices.rolling(window=period).mean()


def extract_latest(series: pd.Series) -> float | None:
    """Get most recent non-NaN value from a series."""
    valid = series.dropna()
    return round(float(valid.iloc[-1]), 4) if not valid.empty else None


def calculate_all_indicators(ticker: str, period: str, indicator_names: list[str]) -> IndicatorSet:
    """Fetch history, compute requested indicators, return IndicatorSet."""
    history = fetch_history(ticker, period)
    closes = history["Close"]

    now = datetime.now(timezone.utc)
    result = IndicatorSet(ticker=ticker.upper(), timestamp=now, period=period)

    if "rsi" in indicator_names:
        rsi_series = calculate_rsi(closes)
        result.rsi = extract_latest(rsi_series)

    if "macd" in indicator_names:
        macd_l, sig_l, hist_l = calculate_macd(closes)
        result.macd = extract_latest(macd_l)
        result.macd_signal = extract_latest(sig_l)
        result.macd_histogram = extract_latest(hist_l)

    if "bollinger" in indicator_names:
        upper, middle, lower = calculate_bollinger_bands(closes)
        result.bollinger_upper = extract_latest(upper)
        result.bollinger_middle = extract_latest(middle)
        result.bollinger_lower = extract_latest(lower)

    if "sma" in indicator_names:
        for p in DEFAULT_SMA_PERIODS:
            sma_val = extract_latest(calculate_sma(closes, p))
            setattr(result, f"sma_{p}", sma_val)

    return result


def main():
    parser = argparse.ArgumentParser(description="Calculate technical indicators for a ticker")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--period", "-p", default=DEFAULT_PERIOD, help="Data period (default: 6mo)")
    parser.add_argument(
        "--indicators", "-i",
        default=",".join(DEFAULT_INDICATORS),
        help="Comma-separated indicators: rsi,macd,bollinger,sma (default: rsi,macd,bollinger)",
    )
    parser.add_argument("--output", "-o", help="Output JSON file path (default: stdout)")
    args = parser.parse_args()

    indicator_names = [name.strip().lower() for name in args.indicators.split(",")]

    try:
        indicator_set = calculate_all_indicators(args.ticker, args.period, indicator_names)
    except Exception as e:
        print(f"Error calculating indicators for {args.ticker}: {e}", file=sys.stderr)
        sys.exit(1)

    json_str = json.dumps(indicator_set.model_dump(), indent=2, default=str, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(json_str, encoding="utf-8")
        print(f"Indicators saved to {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
