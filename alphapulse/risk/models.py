from __future__ import annotations

from pydantic import BaseModel, Field

from alphapulse.core.models import BaseResult


class VolatilityMetrics(BaseModel):
    historical_vol_30d: float | None = None
    historical_vol_90d: float | None = None
    implied_vol_pct: float | None = None
    beta_vs_spy: float | None = None
    correlation_vs_spy: float | None = None


class DrawdownMetrics(BaseModel):
    max_drawdown_1y_pct: float | None = None
    max_drawdown_3y_pct: float | None = None
    avg_drawdown_duration_days: float | None = None
    current_drawdown_pct: float | None = None


class VaRMetrics(BaseModel):
    var_95_daily_pct: float | None = None
    var_99_daily_pct: float | None = None
    expected_shortfall_95_pct: float | None = None


class PositionSizing(BaseModel):
    portfolio_value: float
    method: str
    max_position_pct: float
    recommended_shares: int = 0
    stop_loss_price: float | None = None
    rationale: str = ""


class RiskAssessment(BaseResult):
    symbol: str
    volatility: VolatilityMetrics
    drawdown: DrawdownMetrics
    var: VaRMetrics
    liquidity: dict[str, float] = Field(default_factory=dict)
    event_risks: list[str] = Field(default_factory=list)
    tail_risk_note: str = ""
    position_sizing: PositionSizing | None = None
    risk_score: str = "Moderate Risk"
