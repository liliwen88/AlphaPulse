from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from alphapulse.core.models import BaseResult


class EconomicEvent(BaseModel):
    date: date
    time: str | None = None
    event: str
    period: str | None = None
    consensus: str | None = None
    previous: str | None = None
    impact: str = "Medium"


class FedWatchProbability(BaseModel):
    meeting_date: date
    probabilities: dict[str, float]
    implied_rate: float


class YieldCurve(BaseModel):
    rate_3m: float | None = None
    rate_2y: float | None = None
    rate_5y: float | None = None
    rate_10y: float | None = None
    rate_30y: float | None = None
    spread_2s10s: float | None = None


class MacroRegime(BaseModel):
    fed_funds_rate: float | None = None
    fomc_next: FedWatchProbability | None = None
    inflation_cpi_yoy: float | None = None
    inflation_core_pce_yoy: float | None = None
    unemployment_rate: float | None = None
    gdp_growth_qoq: float | None = None
    yield_curve: YieldCurve | None = None
    dxy: float | None = None
    vix: float | None = None
    wti_crude: float | None = None


class MacroOutlook(BaseResult):
    current_week_events: list[EconomicEvent]
    upcoming_events: list[EconomicEvent]
    regime: MacroRegime
    regime_summary: str = ""
    positioning_implications: str = ""
