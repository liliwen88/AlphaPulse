"""Risk metric computations using pure numpy/pandas."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def compute_historical_volatility(returns: pd.Series, window: int) -> float | None:
    """Annualized historical volatility from log returns."""
    if len(returns) < window:
        return None
    daily_vol = returns.iloc[-window:].std()
    if pd.isna(daily_vol):
        return None
    return round(float(daily_vol * np.sqrt(TRADING_DAYS_PER_YEAR) * 100), 1)


def compute_beta(
    stock_returns: pd.Series,
    market_returns: pd.Series,
) -> float | None:
    """Calculate beta vs market (SPY) using aligned daily returns."""
    common = stock_returns.dropna().index.intersection(market_returns.dropna().index)
    if len(common) < 20:
        return None
    s = stock_returns[common]
    m = market_returns[common]
    cov = s.cov(m)
    var = m.var()
    if var == 0:
        return None
    return round(float(cov / var), 2)


def compute_correlation(
    stock_returns: pd.Series,
    market_returns: pd.Series,
) -> float | None:
    common = stock_returns.dropna().index.intersection(market_returns.dropna().index)
    if len(common) < 20:
        return None
    return round(float(stock_returns[common].corr(market_returns[common])), 2)


def compute_var(
    returns: pd.Series,
    confidence: float = 0.95,
) -> float | None:
    """Value at Risk — the loss at the given confidence level (as a positive %)."""
    clean = returns.dropna()
    if len(clean) < 20:
        return None
    var = float(np.percentile(clean, (1 - confidence) * 100))
    return round(-var * 100, 2)


def compute_expected_shortfall(returns: pd.Series, confidence: float = 0.95) -> float | None:
    """CVaR / Expected Shortfall — average loss beyond VaR."""
    clean = returns.dropna()
    if len(clean) < 20:
        return None
    var_threshold = np.percentile(clean, (1 - confidence) * 100)
    tail = clean[clean <= var_threshold]
    if len(tail) == 0:
        return None
    return round(float(-tail.mean() * 100), 2)


def compute_max_drawdown(prices: pd.Series) -> dict:
    """Compute maximum drawdown from a price series."""
    if len(prices) < 2:
        return {"max_dd_pct": None, "current_dd_pct": None}

    cumulative_max = prices.cummax()
    drawdown = (prices - cumulative_max) / cumulative_max

    max_dd = float(drawdown.min())
    current_dd = float(drawdown.iloc[-1])

    return {
        "max_dd_pct": round(max_dd * 100, 1),
        "current_dd_pct": round(current_dd * 100, 1) if current_dd < 0 else 0.0,
    }
