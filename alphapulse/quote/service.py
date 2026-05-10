from __future__ import annotations

import logging

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataFreshness, DataSource
from alphapulse.quote.models import BatchQuoteResult, StockQuote
from alphapulse.quote.provider import YahooFinanceProvider

logger = logging.getLogger(__name__)


class QuoteService:
    """Service for fetching real-time stock quotes and snapshots."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()
        self._provider = YahooFinanceProvider(self._config)

    async def get(self, symbol: str) -> StockQuote:
        info = await self._provider.get_info(symbol)
        return self._build_quote(symbol.upper(), info)

    async def get_batch(self, symbols: list[str]) -> BatchQuoteResult:
        info_map = await self._provider.get_batch_info(symbols)
        quotes = []
        for sym in symbols:
            info = info_map.get(sym.upper(), {})
            if info:
                quotes.append(self._build_quote(sym.upper(), info))
            else:
                quotes.append(self._empty_quote(sym.upper()))
        freshness = self._provider.freshness()
        return BatchQuoteResult(
            quotes=quotes,
            count=len(quotes),
            data_sources=[DataSource.YAHOO_FINANCE.value],
            data_freshness=[freshness],
        )

    def _build_quote(self, symbol: str, info: dict) -> StockQuote:
        current = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("open") or 0.0
        prev = info.get("previousClose") or info.get("regularMarketPreviousClose") or current
        change = current - prev if current and prev else 0.0
        change_pct = (change / prev * 100) if prev and prev != 0 else 0.0

        freshness = self._provider.freshness()

        return StockQuote(
            symbol=symbol,
            company_name=(
                info.get("longName")
                or info.get("shortName")
                or info.get("displayName")
                or ""
            ),
            exchange=info.get("exchange") or info.get("fullExchangeName") or "",
            current_price=round(current, 2),
            previous_close=round(prev, 2),
            change=round(change, 2),
            change_percent=round(change_pct, 2),
            volume=info.get("volume") or info.get("regularMarketVolume") or 0,
            avg_volume_10d=info.get("averageVolume10days") or info.get("averageDailyVolume10Day"),
            market_cap_billions=(
                round(info.get("marketCap", 0) / 1e9, 2)
                if info.get("marketCap")
                else None
            ),
            pe_ratio_ttm=info.get("trailingPE") or info.get("forwardPE"),
            eps_ttm=info.get("trailingEps"),
            forward_pe=info.get("forwardPE"),
            week_52_high=info.get("fiftyTwoWeekHigh"),
            week_52_low=info.get("fiftyTwoWeekLow"),
            dividend_yield_pct=(
                round(info["dividendYield"] * 100, 2)
                if info.get("dividendYield")
                else None
            ),
            beta=info.get("beta"),
            short_float_pct=(
                round(info["shortPercentOfFloat"] * 100, 2)
                if info.get("shortPercentOfFloat")
                else None
            ),
            currency=info.get("currency", "USD"),
            data_sources=[DataSource.YAHOO_FINANCE.value],
            data_freshness=[freshness],
        )

    @staticmethod
    def _empty_quote(symbol: str) -> StockQuote:
        return StockQuote(
            symbol=symbol,
            current_price=0.0,
            previous_close=0.0,
            change=0.0,
            change_percent=0.0,
            volume=0,
            data_sources=[],
        )
