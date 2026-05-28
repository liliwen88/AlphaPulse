"""Pydantic v2 data models for AlphaPulse."""

from datetime import datetime
from typing import Optional, List, Dict
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
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: float = 0.0
    fifty_two_week_low: float = 0.0
    fifty_two_week_position_pct: float = 0.0
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    momentum: Dict[str, float] = Field(default_factory=lambda: {"1d": 0.0, "1w": 0.0, "1m": 0.0, "3m": 0.0})
    data_source: str = "yfinance"
    data_freshness: str = ""


# ---- Technical Indicators ----

class IndicatorSet(BaseModel):
    """Calculated technical indicators for a ticker."""
    ticker: str
    timestamp: datetime
    period: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None


# ---- News ----

class NewsArticle(BaseModel):
    """A single news article."""
    headline: str
    date: datetime
    source: str
    url: Optional[str] = None
    summary: Optional[str] = None
    impact: str = "Neutral"


class NewsBundle(BaseModel):
    """Aggregated news for a ticker."""
    ticker: str
    fetched_at: datetime
    lookback_days: int
    sources_attempted: List[str] = Field(default_factory=list)
    sources_succeeded: List[str] = Field(default_factory=list)
    articles: List[NewsArticle] = Field(default_factory=list)


# ---- Scoring ----

class DimensionScore(BaseModel):
    """Score for a single analysis dimension."""
    dimension: str
    weight: float
    raw_score: float
    weighted_score: float
    details: List[str] = Field(default_factory=list)


class ScoreResult(BaseModel):
    """Aggregated multi-dimensional scoring."""
    ticker: str
    timestamp: datetime
    overall_score: float
    conviction: str
    dimensions: List[DimensionScore] = Field(default_factory=list)


# ---- Strategy ----

class StrategyResult(BaseModel):
    """Actionable investment strategy output."""
    ticker: str
    timestamp: datetime
    signal: str
    entry_price: Optional[float] = None
    take_profit: Optional[float] = None
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
    market_snapshot: Optional[MarketSnapshot] = None
    indicators: Optional[IndicatorSet] = None
    news: Optional[NewsBundle] = None
    score: Optional[ScoreResult] = None
    strategy: Optional[StrategyResult] = None
    chart_path: Optional[str] = None
    output_dir: str = ""
