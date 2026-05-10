from __future__ import annotations

import asyncio
import logging

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.flow.insider import detect_insider_cluster, get_insider_transactions
from alphapulse.flow.models import InstitutionalFlow
from alphapulse.flow.options_flow import get_options_flow_signals, get_short_interest

logger = logging.getLogger(__name__)


class FlowService:
    """Service for institutional flow analysis — 13F, insider trades, options flow."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()

    async def analyze(self, symbol: str) -> InstitutionalFlow:
        symbol = symbol.strip().upper()

        insider_trades, short_int, options_flow = await asyncio.gather(
            get_insider_transactions(symbol, config=self._config),
            get_short_interest(symbol, config=self._config),
            get_options_flow_signals(symbol, config=self._config),
        )

        cluster = detect_insider_cluster(insider_trades)

        # Build summary
        parts = []
        buy_count = sum(1 for t in insider_trades if t.transaction_type == "Buy")
        sell_count = sum(1 for t in insider_trades if t.transaction_type == "Sell")
        if buy_count or sell_count:
            parts.append(f"Insider: {buy_count} buys, {sell_count} sells (3mo)")

        if cluster:
            parts.append(cluster)

        if short_int:
            if short_int.short_float_pct is not None:
                parts.append(f"Short Float: {short_int.short_float_pct:.1f}% ({short_int.signal})")
            if short_int.days_to_cover is not None:
                parts.append(f"Days to Cover: {short_int.days_to_cover:.1f}")

        if options_flow:
            unusual_count = len(options_flow)
            parts.append(f"Options: {unusual_count} unusual activity signal(s)")

        return InstitutionalFlow(
            symbol=symbol,
            recent_insider_trades=insider_trades[:10],
            insider_cluster_signal=cluster,
            options_flow=options_flow,
            short_interest=short_int,
            summary="\n".join(parts) if parts else "No significant flow signals detected",
            data_sources=[DataSource.YAHOO_FINANCE.value],
        )
