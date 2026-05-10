from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from alphapulse.core.models import BaseResult


class InstitutionalHolding(BaseModel):
    fund_name: str
    filing_date: date | None = None
    shares_held: int | None = None
    value_millions: float | None = None
    change_qoq_pct: float | None = None
    rank: int | None = None


class InsiderTransaction(BaseModel):
    insider_name: str
    title: str
    transaction_date: date
    transaction_type: str  # Buy, Sell, Grant, Exercise
    shares: int
    price: float | None = None
    total_value: float | None = None


class OptionsFlowSignal(BaseModel):
    symbol: str
    date: date | None = None
    type: str  # unusual_call, unusual_put, block_trade
    contracts: int | None = None
    premium: float | None = None
    description: str = ""


class ShortInterest(BaseModel):
    symbol: str
    short_float_pct: float | None = None
    days_to_cover: float | None = None
    change_vs_prior: float | None = None
    signal: str = "moderate"


class InstitutionalFlow(BaseResult):
    symbol: str
    top_holders: list[InstitutionalHolding] = Field(default_factory=list)
    notable_investors: list[InstitutionalHolding] = Field(default_factory=list)
    recent_insider_trades: list[InsiderTransaction] = Field(default_factory=list)
    insider_cluster_signal: str | None = None
    options_flow: list[OptionsFlowSignal] = Field(default_factory=list)
    short_interest: ShortInterest | None = None
    summary: str = ""
