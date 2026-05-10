"""Pure numpy/pandas technical indicator computations. No external TA library needed."""

from __future__ import annotations

import numpy as np
import pandas as pd

from alphapulse.technical.models import (
    BollingerBands,
    MACDResult,
    MovingAverages,
    RSIResult,
)


def compute_sma(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window=window, min_periods=window).mean()


def compute_ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def compute_moving_averages(close: pd.Series) -> MovingAverages:
    last = close.iloc[-1] if len(close) > 0 else 0.0
    sma20 = compute_sma(close, 20).iloc[-1] if len(close) >= 20 else None
    sma50 = compute_sma(close, 50).iloc[-1] if len(close) >= 50 else None
    sma200 = compute_sma(close, 200).iloc[-1] if len(close) >= 200 else None
    ema12 = compute_ema(close, 12).iloc[-1] if len(close) >= 12 else None
    ema26 = compute_ema(close, 26).iloc[-1] if len(close) >= 26 else None

    vs50 = ((last - sma50) / sma50 * 100) if sma50 and sma50 != 0 else None
    vs200 = ((last - sma200) / sma200 * 100) if sma200 and sma200 != 0 else None

    return MovingAverages(
        sma_20=round(sma20, 2) if sma20 is not None else None,
        sma_50=round(sma50, 2) if sma50 is not None else None,
        sma_200=round(sma200, 2) if sma200 is not None else None,
        ema_12=round(ema12, 2) if ema12 is not None else None,
        ema_26=round(ema26, 2) if ema26 is not None else None,
        price_vs_sma_50_pct=round(vs50, 2) if vs50 is not None else None,
        price_vs_sma_200_pct=round(vs200, 2) if vs200 is not None else None,
    )


def compute_macd(close: pd.Series) -> MACDResult:
    ema12 = compute_ema(close, 12)
    ema26 = compute_ema(close, 26)
    macd_line = ema12 - ema26
    signal_line = compute_ema(macd_line, 9)
    histogram = macd_line - signal_line

    last_macd = macd_line.iloc[-1]
    last_signal = signal_line.iloc[-1]
    last_hist = histogram.iloc[-1]
    prev_macd = macd_line.iloc[-2] if len(macd_line) >= 2 else last_macd
    prev_signal = signal_line.iloc[-2] if len(signal_line) >= 2 else last_signal
    prev_hist = histogram.iloc[-2] if len(histogram) >= 2 else last_hist

    # Signal determination
    if prev_macd <= prev_signal and last_macd > last_signal:
        signal = "bullish_crossover"
    elif prev_macd >= prev_signal and last_macd < last_signal:
        signal = "bearish_crossover"
    elif last_macd > 0:
        signal = "above_zero"
    else:
        signal = "below_zero"

    # Divergence check (simple version: histogram vs price momentum)
    divergence = None
    if len(close) >= 20 and len(histogram) >= 20:
        price_momentum = close.iloc[-1] - close.iloc[-20]
        hist_momentum = histogram.iloc[-1] - histogram.iloc[-20]
        if price_momentum < 0 and hist_momentum > 0:
            divergence = "bullish_divergence"
        elif price_momentum > 0 and hist_momentum < 0:
            divergence = "bearish_divergence"

    return MACDResult(
        macd_line=round(last_macd, 4),
        signal_line=round(last_signal, 4),
        histogram=round(last_hist, 4),
        signal=signal,
        divergence=divergence,
    )


def compute_rsi(close: pd.Series, window: int = 14) -> RSIResult:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + rs))
    value = rsi_series.iloc[-1] if len(rsi_series) > 0 else 50.0

    if pd.isna(value):
        value = 50.0

    if value >= 70:
        signal = "overbought"
    elif value <= 30:
        signal = "oversold"
    else:
        signal = "neutral"

    return RSIResult(value=round(value, 1), signal=signal)


def compute_bollinger(close: pd.Series, window: int = 20, num_std: float = 2.0) -> BollingerBands:
    sma = compute_sma(close, window)
    std = close.rolling(window=window, min_periods=window).std()
    upper = sma + num_std * std
    lower = sma - num_std * std

    last_close = close.iloc[-1]
    last_sma = sma.iloc[-1]
    last_upper = upper.iloc[-1]
    last_lower = lower.iloc[-1]
    bandwidth = (last_upper - last_lower) / last_sma if last_sma != 0 else 0.0

    if last_close >= last_upper:
        position = "above_upper"
    elif last_close <= last_lower:
        position = "below_lower"
    else:
        position = "inside"

    # Squeeze detection: bandwidth at 20-period low
    bandwidth_series = (upper - lower) / sma
    squeeze = bool(bandwidth_series.iloc[-1] <= bandwidth_series.iloc[-20:].min()) if len(bandwidth_series) >= 20 else False

    return BollingerBands(
        upper=round(last_upper, 2),
        middle=round(last_sma, 2),
        lower=round(last_lower, 2),
        bandwidth=round(bandwidth, 4),
        position=position,
        squeeze=squeeze,
    )


def compute_atr(df: pd.DataFrame, window: int = 14) -> float | None:
    if len(df) < window + 1:
        return None
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / window, min_periods=window).mean()
    return round(float(atr.iloc[-1]), 2) if len(atr) > 0 else None


def compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.where(close.diff() > 0, 1, np.where(close.diff() < 0, -1, 0))
    return (volume * direction).cumsum()


def compute_volume_profile(df: pd.DataFrame) -> dict:
    volume = int(df["Volume"].iloc[-1]) if len(df) > 0 else 0
    avg_vol = int(df["Volume"].rolling(window=20, min_periods=1).mean().iloc[-1]) if len(df) > 0 else 1
    ratio = volume / avg_vol if avg_vol > 0 else 1.0

    if ratio >= 2.0:
        signal = "heavy"
    elif ratio <= 0.5:
        signal = "light"
    else:
        signal = "normal"

    # OBV divergence
    close = df["Close"]
    vol = df["Volume"]
    obv = compute_obv(close, vol)
    obv_div = False
    if len(obv) >= 20:
        price_up = close.iloc[-1] > close.iloc[-20]
        obv_up = obv.iloc[-1] > obv.iloc[-20]
        if price_up != obv_up:
            obv_div = True

    return {
        "current_volume": volume,
        "avg_volume_20d": avg_vol,
        "volume_ratio": round(ratio, 2),
        "signal": signal,
        "obv_divergence": obv_div,
    }
