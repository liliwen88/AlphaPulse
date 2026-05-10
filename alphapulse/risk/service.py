from __future__ import annotations

import asyncio
import logging

import numpy as np
import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.quote.provider import YahooFinanceProvider
from alphapulse.risk.models import (
    DrawdownMetrics,
    RiskAssessment,
    VaRMetrics,
    VolatilityMetrics,
)
from alphapulse.risk.sizing import vol_targeted_size
from alphapulse.risk.volatility import (
    compute_beta,
    compute_correlation,
    compute_expected_shortfall,
    compute_historical_volatility,
    compute_max_drawdown,
    compute_var,
)

logger = logging.getLogger(__name__)


class RiskService:
    """Service for risk assessment, volatility analysis, and position sizing."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()
        self._provider = YahooFinanceProvider(self._config)

    async def assess(
        self,
        symbol: str,
        portfolio_value: float | None = None,
    ) -> RiskAssessment:
        symbol = symbol.strip().upper()

        # Fetch stock and SPY data in parallel
        stock_df, spy_df, info = await asyncio.gather(
            self._provider.get_history(symbol, period="3y", interval="1d"),
            self._provider.get_history("SPY", period="3y", interval="1d"),
            self._provider.get_info(symbol),
            return_exceptions=True,
        )

        if isinstance(stock_df, Exception):
            raise ValueError(f"Failed to fetch data for {symbol}: {stock_df}")
        if isinstance(spy_df, Exception):
            spy_df = None
        if isinstance(info, Exception):
            info = {}

        stock_returns = stock_df["Close"].pct_change().dropna()
        spy_returns = None
        if spy_df is not None and not spy_df.empty:
            spy_returns = spy_df["Close"].pct_change().dropna()

        # Volatility
        vol30 = compute_historical_volatility(stock_returns, 30)
        vol90 = compute_historical_volatility(stock_returns, 90)
        beta = compute_beta(stock_returns, spy_returns) if spy_returns is not None else None
        corr = compute_correlation(stock_returns, spy_returns) if spy_returns is not None else None

        vol = VolatilityMetrics(
            historical_vol_30d=vol30,
            historical_vol_90d=vol90,
            beta_vs_spy=beta,
            correlation_vs_spy=corr,
        )

        # Drawdown
        dd_1y = compute_max_drawdown(stock_df["Close"].iloc[-252:]) if len(stock_df) >= 252 else {}
        dd_3y = compute_max_drawdown(stock_df["Close"]) if len(stock_df) >= 756 else {}

        drawdown = DrawdownMetrics(
            max_drawdown_1y_pct=dd_1y.get("max_dd_pct"),
            max_drawdown_3y_pct=dd_3y.get("max_dd_pct"),
            current_drawdown_pct=dd_1y.get("current_dd_pct"),
        )

        # VaR
        var95 = compute_var(stock_returns, 0.95)
        var99 = compute_var(stock_returns, 0.99)
        es95 = compute_expected_shortfall(stock_returns, 0.95)

        var_metrics = VaRMetrics(
            var_95_daily_pct=var95,
            var_99_daily_pct=var99,
            expected_shortfall_95_pct=es95,
        )

        # Liquidity
        avg_volume = int(stock_df["Volume"].tail(20).mean()) if len(stock_df) >= 20 else 0
        avg_price = float(stock_df["Close"].iloc[-1])
        dollar_volume = avg_volume * avg_price
        liquidity = {
            "avg_daily_volume": avg_volume,
            "avg_dollar_volume_millions": round(dollar_volume / 1e6, 2),
            "current_price": avg_price,
        }

        # Event risks
        earnings = info.get("earningsDate")
        event_risks = []
        if earnings:
            event_risks.append("Upcoming earnings — elevated event risk")
        if beta and beta > 2.0:
            event_risks.append(f"High beta ({beta:.1f}) — amplified market moves")
        if vol30 and vol30 > 60:
            event_risks.append(f"Extreme volatility ({vol30:.0f}% annualized)")

        # Tail risk
        tail_note = (
            f"In a 2σ move (~{round(vol30 * 2, 0) if vol30 else '?'}%), "
            f"this stock could swing ±${round(avg_price * 2 * (vol30 or 30) / 100 / np.sqrt(252), 2)} "
            f"in a single day."
        )

        # Position sizing
        sizing = None
        if portfolio_value and vol30 and avg_price > 0:
            sizing = vol_targeted_size(
                portfolio_value=portfolio_value,
                annualized_vol=vol30 / 100,
                current_price=avg_price,
            )

        # Risk score
        score = 0
        if vol30 and vol30 > 50:
            score += 2
        elif vol30 and vol30 > 30:
            score += 1
        if beta and beta > 1.5:
            score += 1
        if var95 and var95 > 3:
            score += 1
        if not liquidity["avg_dollar_volume_millions"] or liquidity["avg_dollar_volume_millions"] < 10:
            score += 1

        if score >= 4:
            risk_score = "Speculative"
        elif score >= 2:
            risk_score = "High Risk"
        elif score >= 1:
            risk_score = "Moderate Risk"
        else:
            risk_score = "Low Risk"

        freshness = self._provider.freshness()

        return RiskAssessment(
            symbol=symbol,
            volatility=vol,
            drawdown=drawdown,
            var=var_metrics,
            liquidity=liquidity,
            event_risks=event_risks,
            tail_risk_note=tail_note,
            position_sizing=sizing,
            risk_score=risk_score,
            data_sources=[DataSource.YAHOO_FINANCE.value],
            data_freshness=[freshness],
        )
