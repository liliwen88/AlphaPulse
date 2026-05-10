from __future__ import annotations

import asyncio
import logging

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.core.models import DataSource
from alphapulse.hotspots.indices import get_major_indices
from alphapulse.hotspots.models import MarketHotspots
from alphapulse.hotspots.screener import (
    get_sector_performance,
    get_top_movers,
    get_unusual_volume,
)

logger = logging.getLogger(__name__)


class HotspotService:
    """Service for scanning market hotspots, sector rotation, and unusual activity."""

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()

    async def scan(self) -> MarketHotspots:
        indices, sectors, (gainers, losers), unusual = await asyncio.gather(
            get_major_indices(self._config),
            get_sector_performance(self._config),
            get_top_movers(config=self._config),
            get_unusual_volume(config=self._config),
        )

        vix = None
        for idx in indices:
            if idx.symbol == "^VIX":
                vix = idx.price
                break

        # Sector rotation signal
        best_sector = sectors[0] if sectors else None
        worst_sector = sectors[-1] if sectors else None

        summary_parts = ["Market summary:"]

        spx = next((i for i in indices if i.symbol == "^GSPC"), None)
        if spx:
            direction = "up" if spx.change_pct > 0 else "down"
            summary_parts.append(
                f"S&P 500 {direction} {abs(spx.change_pct):.2f}% to {spx.price:.0f}"
            )

        if best_sector:
            summary_parts.append(
                f"Leading: {best_sector.sector} ({best_sector.change_pct_day:+.2f}%)"
            )
        if worst_sector:
            summary_parts.append(
                f"Lagging: {worst_sector.sector} ({worst_sector.change_pct_day:+.2f}%)"
            )
        if vix:
            vix_level = "elevated" if vix > 25 else "moderate" if vix > 15 else "low"
            summary_parts.append(f"VIX={vix:.1f} ({vix_level})")

        thematic = {
            "AI & Semis": _thematic_pct(["NVDA", "AMD", "INTC", "QCOM", "SMH"], gainers, losers),
            "Mega Cap Tech": _thematic_pct(["AAPL", "MSFT", "GOOGL", "META", "AMZN"], gainers, losers),
            "Energy": _thematic_pct(["XOM", "CVX", "COP", "OXY", "DVN"], gainers, losers),
            "Crypto Related": _thematic_pct(["COIN", "MARA", "RIOT", "SQ"], gainers, losers),
            "Meme Stocks": _thematic_pct(["GME", "AMC", "PLTR"], gainers, losers),
        }

        return MarketHotspots(
            indices=indices,
            vix=vix,
            sector_performance=sectors,
            top_gainers=gainers,
            top_losers=losers,
            unusual_volume=unusual,
            thematic_baskets={k: v for k, v in thematic.items() if v != 0},
            summary="\n".join(summary_parts),
            data_sources=[DataSource.YAHOO_FINANCE.value],
        )


def _thematic_pct(
    tickers: list[str],
    gainers: list,
    losers: list,
) -> float:
    all_movers = {m.symbol: m.change_pct for m in gainers + losers}
    pcts = [all_movers.get(t, 0.0) for t in tickers]
    pcts = [p for p in pcts if p != 0.0]
    return round(sum(pcts) / len(pcts), 2) if pcts else 0.0
