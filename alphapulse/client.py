"""Top-level facade classes for the AlphaPulse SDK."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from alphapulse.core.config import AlphaPulseConfig

if TYPE_CHECKING:
    from alphapulse.flow.service import FlowService
    from alphapulse.fundamentals.service import FundamentalService
    from alphapulse.hotspots.service import HotspotService
    from alphapulse.macro.service import MacroService
    from alphapulse.quote.service import QuoteService
    from alphapulse.risk.service import RiskService
    from alphapulse.technical.service import TechnicalService


class AlphaPulse:
    """Async client for AlphaPulse SDK.

    Usage:
        ap = AlphaPulse()
        quote = await ap.quote.get("AAPL")
        fundamentals = await ap.fundamentals.analyze("AAPL")
    """

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._config = config or AlphaPulseConfig()
        self._quote: QuoteService | None = None
        self._fundamentals: FundamentalService | None = None
        self._technical: TechnicalService | None = None
        self._hotspots: HotspotService | None = None
        self._macro: MacroService | None = None
        self._flow: FlowService | None = None
        self._risk: RiskService | None = None

    @property
    def quote(self) -> QuoteService:
        if self._quote is None:
            from alphapulse.quote.service import QuoteService

            self._quote = QuoteService(self._config)
        return self._quote

    @property
    def fundamentals(self) -> FundamentalService:
        if self._fundamentals is None:
            from alphapulse.fundamentals.service import FundamentalService

            self._fundamentals = FundamentalService(self._config)
        return self._fundamentals

    @property
    def technical(self) -> TechnicalService:
        if self._technical is None:
            from alphapulse.technical.service import TechnicalService

            self._technical = TechnicalService(self._config)
        return self._technical

    @property
    def hotspots(self) -> HotspotService:
        if self._hotspots is None:
            from alphapulse.hotspots.service import HotspotService

            self._hotspots = HotspotService(self._config)
        return self._hotspots

    @property
    def macro(self) -> MacroService:
        if self._macro is None:
            from alphapulse.macro.service import MacroService

            self._macro = MacroService(self._config)
        return self._macro

    @property
    def flow(self) -> FlowService:
        if self._flow is None:
            from alphapulse.flow.service import FlowService

            self._flow = FlowService(self._config)
        return self._flow

    @property
    def risk(self) -> RiskService:
        if self._risk is None:
            from alphapulse.risk.service import RiskService

            self._risk = RiskService(self._config)
        return self._risk


class AlphaPulseSync:
    """Synchronous wrapper around AlphaPulse. Runs async methods via asyncio.run().

    Usage:
        ap = AlphaPulseSync()
        result = ap.quote.get("AAPL")
    """

    def __init__(self, config: AlphaPulseConfig | None = None) -> None:
        self._async = AlphaPulse(config)

    @property
    def quote(self) -> QuoteService:
        return self._async.quote

    @property
    def fundamentals(self) -> FundamentalService:
        return self._async.fundamentals

    @property
    def technical(self) -> TechnicalService:
        return self._async.technical

    @property
    def hotspots(self) -> HotspotService:
        return self._async.hotspots

    @property
    def macro(self) -> MacroService:
        return self._async.macro

    @property
    def flow(self) -> FlowService:
        return self._async.flow

    @property
    def risk(self) -> RiskService:
        return self._async.risk
