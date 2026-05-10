from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.flow.models import InsiderTransaction

logger = logging.getLogger(__name__)


async def get_insider_transactions(
    symbol: str,
    months: int = 3,
    config: AlphaPulseConfig | None = None,
) -> list[InsiderTransaction]:
    """Fetch recent insider transactions from Yahoo Finance."""
    try:
        t = await asyncio.to_thread(lambda: yf.Ticker(symbol))
        insider = await asyncio.to_thread(lambda: t.insider_transactions)
        if insider is None or (hasattr(insider, "empty") and insider.empty):
            return []
        results = []
        for _, row in insider.head(20).iterrows():
            try:
                tx_type = str(row.get("startDate") or "")
                # yfinance insider_transactions structure varies; extract what we can
                results.append(InsiderTransaction(
                    insider_name=str(row.get("filerName", "")),
                    title=str(row.get("filerRelation", "")),
                    transaction_date=row.get("startDate") if hasattr(row.get("startDate"), "date") else None,
                    transaction_type=_classify_type(row),
                    shares=int(row.get("shares", 0)) if row.get("shares") else 0,
                    price=float(row.get("price", 0)) if row.get("price") else None,
                    total_value=(
                        float(row.get("value", 0)) if row.get("value")
                        else (float(row.get("shares", 0)) * float(row.get("price", 0))
                              if row.get("shares") and row.get("price") else None)
                    ),
                ))
            except Exception:
                continue
        return results
    except Exception as e:
        logger.warning(f"Failed to fetch insider transactions for {symbol}: {e}")
        return []


def detect_insider_cluster(transactions: list[InsiderTransaction]) -> str | None:
    """Detect if multiple insiders are buying/selling in a short window."""
    buys = [t for t in transactions if t.transaction_type == "Buy"]
    sells = [t for t in transactions if t.transaction_type == "Sell"]
    if len(buys) >= 3:
        return f"Cluster buying: {len(buys)} insiders purchased recently"
    if len(sells) >= 3:
        return f"Cluster selling: {len(sells)} insiders sold recently"
    return None


def _classify_type(row) -> str:
    text = str(row.to_dict()).lower()
    if "sale" in text or "sell" in text:
        return "Sell"
    if "purchase" in text or "buy" in text:
        return "Buy"
    if "grant" in text or "award" in text:
        return "Grant"
    if "exercise" in text or "option" in text:
        return "Exercise"
    return "Unknown"
