"""Pydantic v2 data models for AlphaPulse."""

from datetime import datetime
from pydantic import BaseModel, Field


# ---- Market Data ----

class MarketSnapshot(BaseModel):
    """Point-in-time market data snapshot for a single ticker."""
    ticker: str
    timestamp: datetime
    current_price: float
    previous_close: float
    day_change_pct: float
    volume: int
    avg_volume: int = 0
    volume_ratio: float = 0.0
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    fifty_two_week_high: float = 0.0
    fifty_two_week_low: float = 0.0
    fifty_two_week_position_pct: float = 0.0
    support_level: float | None = None
    resistance_level: float | None = None
    momentum: dict[str, float] = Field(default_factory=lambda: {"1d": 0.0, "1w": 0.0, "1m": 0.0, "3m": 0.0})
    data_source: str = "yfinance"
    data_freshness: str = ""


# ---- Technical Indicators ----

class IndicatorSet(BaseModel):
    """Calculated technical indicators for a ticker."""
    ticker: str
    timestamp: datetime
    period: str
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    bollinger_upper: float | None = None
    bollinger_middle: float | None = None
    bollinger_lower: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    sma_200: float | None = None


# ---- News ----

class NewsArticle(BaseModel):
    """A single news article."""
    headline: str
    date: datetime
    source: str
    url: str | None = None
    summary: str | None = None
    impact: str = "Neutral"


class NewsBundle(BaseModel):
    """Aggregated news for a ticker."""
    ticker: str
    fetched_at: datetime
    lookback_days: int
    sources_attempted: list[str] = Field(default_factory=list)
    sources_succeeded: list[str] = Field(default_factory=list)
    articles: list[NewsArticle] = Field(default_factory=list)


# ---- Scoring ----

class DimensionScore(BaseModel):
    """Score for a single analysis dimension."""
    dimension: str
    weight: float
    raw_score: float
    weighted_score: float
    details: list[str] = Field(default_factory=list)


class ScoreResult(BaseModel):
    """Aggregated multi-dimensional scoring."""
    ticker: str
    timestamp: datetime
    overall_score: float
    conviction: str
    dimensions: list[DimensionScore] = Field(default_factory=list)


# ---- Strategy ----

class StrategyResult(BaseModel):
    """Actionable investment strategy output."""
    ticker: str
    timestamp: datetime
    signal: str
    entry_price: float | None = None
    take_profit: float | None = None
    stop_loss: float = 0.0
    position_size_pct: float = 5.0
    rationale: str = ""


# ---- Full Report ----

class AnalysisReport(BaseModel):
    """Top-level container for a complete analysis."""
    ticker: str
    analysis_date: datetime
    data_freshness: str = ""
    conviction: str = ""
    market_snapshot: MarketSnapshot | None = None
    indicators: IndicatorSet | None = None
    news: NewsBundle | None = None
    score: ScoreResult | None = None
    strategy: StrategyResult | None = None
    chart_path: str | None = None
    output_dir: str = ""
