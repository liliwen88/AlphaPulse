"""Support and resistance level detection from price data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from alphapulse.core.models import PriceLevel


def find_swing_highs(high: pd.Series, window: int = 5) -> list[float]:
    """Detect local maxima (swing highs)."""
    if len(high) < window * 2 + 1:
        return []
    highs = []
    for i in range(window, len(high) - window):
        if high.iloc[i] == high.iloc[i - window : i + window + 1].max():
            highs.append(float(high.iloc[i]))
    return highs


def find_swing_lows(low: pd.Series, window: int = 5) -> list[float]:
    """Detect local minima (swing lows)."""
    if len(low) < window * 2 + 1:
        return []
    lows = []
    for i in range(window, len(low) - window):
        if low.iloc[i] == low.iloc[i - window : i + window + 1].min():
            lows.append(float(low.iloc[i]))
    return lows


def cluster_levels(
    levels: list[float],
    threshold: float = 0.02,
    min_cluster_size: int = 2,
) -> list[PriceLevel]:
    """Group nearby price levels into clusters.

    Args:
        levels: List of raw price levels.
        threshold: Price proximity threshold as a fraction (0.02 = 2%).
        min_cluster_size: Minimum number of levels to form a cluster.
    """
    if not levels:
        return []

    sorted_levels = sorted(set(levels))
    clusters: list[list[float]] = []

    for price in sorted_levels:
        if not clusters:
            clusters.append([price])
            continue
        last_cluster = clusters[-1]
        if abs(price - np.mean(last_cluster)) / max(abs(np.mean(last_cluster)), 0.01) <= threshold:
            last_cluster.append(price)
        else:
            clusters.append([price])

    result = []
    for cluster in clusters:
        if len(cluster) >= min_cluster_size:
            avg = round(float(np.mean(cluster)), 2)
            strength = "major" if len(cluster) >= 3 else "minor"
            description = f"Cluster of {len(cluster)} touches around {avg}"
            result.append(PriceLevel(price=avg, type="support", strength=strength, description=description))

    return result


def detect_support_resistance(
    df: pd.DataFrame,
    current_price: float,
    swing_window: int = 5,
    cluster_threshold: float = 0.02,
) -> dict:
    """Detect support and resistance levels from a DataFrame with OHLCV data."""
    highs = find_swing_highs(df["High"], swing_window)
    lows = find_swing_lows(df["Low"], swing_window)

    resistance_levels = cluster_levels(highs, threshold=cluster_threshold)
    support_levels = cluster_levels(lows, threshold=cluster_threshold)

    for lvl in resistance_levels:
        lvl.type = "resistance"
        lvl.description = lvl.description.replace("support", "resistance")

    # Find nearest support and resistance
    supports_below = [s for s in support_levels if s.price < current_price]
    resistances_above = [r for r in resistance_levels if r.price > current_price]

    nearest_support = supports_below[0] if supports_below else None
    nearest_resistance = resistances_above[0] if resistances_above else None

    return {
        "supports": support_levels,
        "resistances": resistance_levels,
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance,
    }
