from __future__ import annotations

import asyncio
import logging
from datetime import date

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.macro.calendar import get_current_week_events, get_upcoming_events
from alphapulse.macro.fed import (
    get_dxy,
    get_fed_funds_rate,
    get_vix,
    get_wti_crude,
    get_yield_curve,
)
from alphapulse.macro.fred import get_cpi_yoy, get_gdp, get_pce, get_unemployment
from alphapulse.macro.models import MacroOutlook, MacroRegime

logger = logging.getLogger(__name__)


class MacroService:
    """Service for macro calendar, regime analysis, and positioning guidance."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()

    async def outlook(self) -> MacroOutlook:
        today = date.today()
        week_events = get_current_week_events(today)
        upcoming = get_upcoming_events(30, today)

        # Fetch macro data in parallel
        (
            fed_rate,
            yield_curve,
            cpi,
            pce,
            unemp,
            gdp,
            dxy,
            vix,
            wti,
        ) = await asyncio.gather(
            get_fed_funds_rate(self._config),
            get_yield_curve(self._config),
            get_cpi_yoy(self._config),
            get_pce(self._config),
            get_unemployment(self._config),
            get_gdp(self._config),
            get_dxy(self._config),
            get_vix(self._config),
            get_wti_crude(self._config),
        )

        regime = MacroRegime(
            fed_funds_rate=fed_rate,
            inflation_cpi_yoy=cpi,
            inflation_core_pce_yoy=pce,
            unemployment_rate=unemp,
            gdp_growth_qoq=gdp,
            yield_curve=yield_curve,
            dxy=dxy,
            vix=vix,
            wti_crude=wti,
        )

        regime_summary = self._build_regime_summary(regime)
        positioning = self._build_positioning(regime)

        sources = [DataSource.YAHOO_FINANCE.value]
        if self._config.fred_api_key:
            sources.append(DataSource.FRED.value)

        return MacroOutlook(
            current_week_events=week_events,
            upcoming_events=upcoming,
            regime=regime,
            regime_summary=regime_summary,
            positioning_implications=positioning,
            data_sources=sources,
        )

    @staticmethod
    def _build_regime_summary(regime: MacroRegime) -> str:
        parts = []

        if regime.fed_funds_rate is not None:
            parts.append(f"Fed Funds Rate: {regime.fed_funds_rate:.2f}%")

        if regime.inflation_cpi_yoy is not None:
            trend = "elevated" if regime.inflation_cpi_yoy > 3 else "moderate" if regime.inflation_cpi_yoy > 2 else "low"
            parts.append(f"CPI YoY: {regime.inflation_cpi_yoy}% ({trend})")

        if regime.unemployment_rate is not None:
            parts.append(f"Unemployment: {regime.unemployment_rate}%")

        if regime.yield_curve and regime.yield_curve.spread_2s10s is not None:
            spread = regime.yield_curve.spread_2s10s
            shape = "inverted" if spread < 0 else "flattening" if spread < 0.5 else "normal"
            parts.append(f"2s10s Spread: {spread:.2f}% ({shape})")

        if regime.vix is not None:
            vol = "elevated" if regime.vix > 25 else "moderate" if regime.vix > 15 else "low"
            parts.append(f"VIX: {regime.vix:.0f} ({vol})")

        if regime.dxy is not None:
            parts.append(f"DXY: {regime.dxy:.1f}")

        if regime.wti_crude is not None:
            parts.append(f"WTI: ${regime.wti_crude:.1f}")

        return "\n".join(parts)

    @staticmethod
    def _build_positioning(regime: MacroRegime) -> str:
        implications = []

        if regime.yield_curve and regime.yield_curve.spread_2s10s is not None:
            if regime.yield_curve.spread_2s10s < 0:
                implications.append(
                    "Inverted yield curve signals recession risk — favor defensive sectors "
                    "(Healthcare, Consumer Staples, Utilities) and maintain higher cash allocation."
                )
            else:
                implications.append(
                    "Normal yield curve supports cyclical exposure — consider "
                    "Financials, Industrials, and Consumer Discretionary."
                )

        if regime.vix is not None:
            if regime.vix > 25:
                implications.append(
                    "Elevated VIX — expect wider swings. Reduce position sizes, "
                    "widen stop losses, consider hedging with VIX calls or put spreads."
                )
            elif regime.vix < 15:
                implications.append(
                    "Low VIX — favorable for risk-on positioning. "
                    "Consider leverage (options, futures) but size conservatively."
                )

        if regime.dxy is not None:
            if regime.dxy > 105:
                implications.append(
                    "Strong USD — headwind for multinationals and emerging markets. "
                    "Favor domestic-focused US companies."
                )

        if regime.wti_crude is not None:
            if regime.wti_crude > 85:
                implications.append(
                    "Elevated oil — supports Energy sector but pressures "
                    "transportation and consumer discretionary (higher input + fuel costs)."
                )

        if not implications:
            implications.append(
                "Macro data incomplete — position neutrally until clearer signals emerge."
            )

        return "\n".join(implications)
