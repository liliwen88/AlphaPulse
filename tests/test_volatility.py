"""Tests for risk/volatility computations."""

import numpy as np
import pandas as pd

from alphapulse.risk.volatility import (
    compute_beta,
    compute_correlation,
    compute_expected_shortfall,
    compute_historical_volatility,
    compute_max_drawdown,
    compute_var,
)


def _make_returns(n=252, mean=0.0, std=0.015):
    np.random.seed(42)
    return pd.Series(np.random.normal(mean, std, n))


class TestHistoricalVol:
    def test_positive(self):
        returns = _make_returns(100)
        vol = compute_historical_volatility(returns, 30)
        assert vol is not None and vol > 0

    def test_insufficient_data(self):
        returns = _make_returns(10)
        vol = compute_historical_volatility(returns, 30)
        assert vol is None


class TestBeta:
    def test_perfect_correlation(self):
        market = _make_returns(100, 0.0, 0.01)
        stock = market * 1.5
        beta = compute_beta(stock, market)
        assert beta is not None
        assert abs(beta - 1.5) < 0.01

    def test_insufficient_data(self):
        s = pd.Series([0.01, -0.01])
        m = pd.Series([0.02, -0.02])
        beta = compute_beta(s, m)
        assert beta is None


class TestVaR:
    def test_95_var(self):
        returns = _make_returns(252)
        var = compute_var(returns, 0.95)
        assert var is not None and var > 0

    def test_99_var_higher_than_95(self):
        returns = _make_returns(252)
        var95 = compute_var(returns, 0.95)
        var99 = compute_var(returns, 0.99)
        assert var99 is not None and var95 is not None
        assert var99 >= var95  # 99% VaR should be more extreme


class TestMaxDrawdown:
    def test_declining_market(self):
        prices = pd.Series([100, 95, 90, 85, 80, 95, 100])
        dd = compute_max_drawdown(prices)
        assert dd["max_dd_pct"] is not None
        assert dd["max_dd_pct"] < 0

    def test_rising_market(self):
        prices = pd.Series([100, 105, 110, 115, 120])
        dd = compute_max_drawdown(prices)
        assert dd["max_dd_pct"] == 0.0 or (dd["max_dd_pct"] is not None and dd["max_dd_pct"] >= 0)


class TestExpectedShortfall:
    def test_positive(self):
        returns = _make_returns(252)
        es = compute_expected_shortfall(returns, 0.95)
        assert es is not None and es > 0

    def test_es_higher_than_var(self):
        returns = _make_returns(252)
        var95 = compute_var(returns, 0.95)
        es95 = compute_expected_shortfall(returns, 0.95)
        assert es95 is not None and var95 is not None
        assert es95 >= var95
