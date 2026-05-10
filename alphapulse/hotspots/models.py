from __future__ import annotations

from pydantic import BaseModel

from alphapulse.core.models import BaseResult


class MarketIndexSnapshot(BaseModel):
    symbol: str
    name: str
    price: float
    change_pct: float
    ytd_change_pct: float | None = None


class SectorPerformance(BaseModel):
    sector: str
    etf_symbol: str
    change_pct_day: float
    change_pct_week: float | None = None
    change_pct_month: float | None = None
    rotation_signal: str | None = None


class TopMover(BaseModel):
    symbol: str
    company_name: str
    price: float
    change_pct: float
    volume: int
    volume_vs_avg_pct: float | None = None


class MarketHotspots(BaseResult):
    indices: list[MarketIndexSnapshot]
    vix: float | None = None
    sector_performance: list[SectorPerformance]
    top_gainers: list[TopMover]
    top_losers: list[TopMover]
    unusual_volume: list[TopMover]
    thematic_baskets: dict[str, float] = {}
    summary: str = ""
