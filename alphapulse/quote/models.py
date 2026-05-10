from __future__ import annotations

from pydantic import BaseModel, Field

from alphapulse.core.models import BaseResult, DataFreshness


class StockQuote(BaseResult):
    """Real-time stock quote and key statistics."""

    symbol: str
    company_name: str = ""
    exchange: str = ""
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    avg_volume_10d: int | None = None
    market_cap_billions: float | None = None
    pe_ratio_ttm: float | None = None
    eps_ttm: float | None = None
    forward_pe: float | None = None
    week_52_high: float | None = None
    week_52_low: float | None = None
    dividend_yield_pct: float | None = None
    beta: float | None = None
    short_float_pct: float | None = None
    currency: str = "USD"


class BatchQuoteResult(BaseResult):
    quotes: list[StockQuote]
    count: int
