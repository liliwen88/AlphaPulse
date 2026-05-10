from __future__ import annotations

import logging

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.quote.provider import YahooFinanceProvider
from alphapulse.technical.indicators import (
    compute_atr,
    compute_bollinger,
    compute_macd,
    compute_moving_averages,
    compute_rsi,
    compute_volume_profile,
)
from alphapulse.technical.levels import detect_support_resistance
from alphapulse.technical.models import TechnicalAnalysis, VolumeProfile, SupportResistanceLevels

logger = logging.getLogger(__name__)


class TechnicalService:
    """Service for technical analysis of stocks."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()
        self._provider = YahooFinanceProvider(self._config)

    async def analyze(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> TechnicalAnalysis:
        df = await self._provider.get_history(symbol, period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No price data available for {symbol}")

        close = df["Close"]
        current_price = round(float(close.iloc[-1]), 2)

        ma = compute_moving_averages(close)
        macd = compute_macd(close)
        rsi = compute_rsi(close)
        bb = compute_bollinger(close)
        atr = compute_atr(df)
        levels_data = detect_support_resistance(df, current_price)
        vol_data = compute_volume_profile(df)

        volume = VolumeProfile(
            current_volume=vol_data["current_volume"],
            avg_volume_20d=vol_data["avg_volume_20d"],
            volume_ratio=vol_data["volume_ratio"],
            signal=vol_data["signal"],
            obv_divergence=vol_data["obv_divergence"],
        )

        levels = SupportResistanceLevels(
            supports=levels_data.get("supports", []),
            resistances=levels_data.get("resistances", []),
            nearest_support=levels_data.get("nearest_support"),
            nearest_resistance=levels_data.get("nearest_resistance"),
        )

        posture, posture_detail = self._determine_posture(ma, macd, rsi, bb, current_price, levels)

        freshness = self._provider.freshness()

        return TechnicalAnalysis(
            symbol=symbol.upper(),
            period=period,
            interval=interval,
            current_price=current_price,
            moving_averages=ma,
            macd=macd,
            rsi=rsi,
            bollinger=bb,
            atr=atr,
            levels=levels,
            volume=volume,
            posture=posture,
            posture_detail=posture_detail,
            data_sources=[DataSource.YAHOO_FINANCE.value],
            data_freshness=[freshness],
        )

    @staticmethod
    def _determine_posture(ma, macd, rsi, bb, current_price, levels):
        signals = []

        # Moving average signals
        if ma.sma_50 is not None:
            signals.append("Bullish" if current_price > ma.sma_50 else "Bearish")
        if ma.sma_200 is not None:
            signals.append("Bullish" if current_price > ma.sma_200 else "Bearish")

        # MACD signal
        if "bullish" in (macd.signal or ""):
            signals.append("Bullish")
        elif "bearish" in (macd.signal or ""):
            signals.append("Bearish")

        # RSI signal
        if rsi.signal == "oversold":
            signals.append("Bullish")
        elif rsi.signal == "overbought":
            signals.append("Bearish")
        else:
            signals.append("Neutral")

        # Bollinger signal
        if bb.position == "below_lower":
            signals.append("Bullish")
        elif bb.position == "above_upper":
            signals.append("Bearish")
        else:
            signals.append("Neutral")

        bull = signals.count("Bullish")
        bear = signals.count("Bearish")

        if bull > bear:
            posture = "Bullish"
        elif bear > bull:
            posture = "Bearish"
        else:
            posture = "Neutral/Rangebound"

        detail_parts = [
            f"Price ${current_price}",
            f"vs SMA50=${ma.sma_50}" if ma.sma_50 else "",
            f"RSI={rsi.value}({rsi.signal})",
            f"MACD={macd.signal}",
        ]
        detail = " | ".join(p for p in detail_parts if p)

        if levels.nearest_support:
            detail += f" | Support=${levels.nearest_support.price}"
        if levels.nearest_resistance:
            detail += f" | Resistance=${levels.nearest_resistance.price}"

        return posture, detail
