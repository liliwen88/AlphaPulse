from __future__ import annotations

from pydantic import BaseModel, Field

from alphapulse.core.models import BaseResult, PriceLevel


class MovingAverages(BaseModel):
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None
    ema_12: float | None = None
    ema_26: float | None = None
    price_vs_sma_50_pct: float | None = None
    price_vs_sma_200_pct: float | None = None


class MACDResult(BaseModel):
    macd_line: float
    signal_line: float
    histogram: float
    signal: str  # bullish_crossover, bearish_crossover, above_zero, below_zero
    divergence: str | None = None


class RSIResult(BaseModel):
    value: float
    signal: str  # overbought, oversold, neutral


class BollingerBands(BaseModel):
    upper: float
    middle: float
    lower: float
    bandwidth: float
    position: str  # above_upper, inside, below_lower
    squeeze: bool = False


class SupportResistanceLevels(BaseModel):
    supports: list[PriceLevel] = Field(default_factory=list)
    resistances: list[PriceLevel] = Field(default_factory=list)
    nearest_support: PriceLevel | None = None
    nearest_resistance: PriceLevel | None = None


class VolumeProfile(BaseModel):
    current_volume: int
    avg_volume_20d: int
    volume_ratio: float
    signal: str  # heavy, normal, light
    obv_divergence: bool = False


class TechnicalAnalysis(BaseResult):
    symbol: str
    period: str
    interval: str
    current_price: float
    moving_averages: MovingAverages
    macd: MACDResult
    rsi: RSIResult
    bollinger: BollingerBands
    atr: float | None = None
    levels: SupportResistanceLevels
    volume: VolumeProfile
    posture: str  # Bullish, Bearish, Neutral/Rangebound
    posture_detail: str = ""
