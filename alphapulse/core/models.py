from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from alphapulse.core.disclaimer import RISK_DISCLAIMER


class DataSource(str, Enum):
    YAHOO_FINANCE = "yahoo_finance"
    SEC_EDGAR = "sec_edgar"
    FRED = "fred"
    CME_FEDWATCH = "cme_fedwatch"
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    CNBC = "cnbc"
    MARKETWATCH = "marketwatch"
    TRADINGVIEW = "tradingview"
    FINVIZ = "finviz"
    WHALEWISDOM = "whalewisdom"
    DATAROMA = "dataroma"
    MORNINGSTAR = "morningstar"
    MACROTRENDS = "macrotrends"
    ETF_COM = "etf_com"
    BARCHART = "barchart"
    MARKET_CHAMELEON = "market_chameleon"


class TimeFrame(str, Enum):
    D1 = "1d"
    D5 = "5d"
    M1 = "1mo"
    M3 = "3mo"
    M6 = "6mo"
    Y1 = "1y"
    Y5 = "5y"
    MAX = "max"


class Market(str, Enum):
    US = "US"
    GLOBAL = "Global"


class PriceLevel(BaseModel):
    price: float
    type: Literal["support", "resistance"]
    strength: Literal["major", "minor"]
    description: str = ""


class DataFreshness(BaseModel):
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: DataSource
    is_stale: bool = False
    stale_reason: str | None = None


class BaseResult(BaseModel):
    """Base class for all analysis results. Every result carries a mandatory risk disclaimer."""

    disclaimer: str = Field(default=RISK_DISCLAIMER, frozen=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_sources: list[str] = Field(default_factory=list)
    data_freshness: list[DataFreshness] = Field(default_factory=list)
