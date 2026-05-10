from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.flow.models import OptionsFlowSignal, ShortInterest

logger = logging.getLogger(__name__)


async def get_short_interest(
    symbol: str,
    config: AlphaPulseConfig | None = None,
) -> ShortInterest | None:
    """Fetch short interest data from Yahoo Finance."""
    try:
        t = await asyncio.to_thread(lambda: yf.Ticker(symbol))
        info = await asyncio.to_thread(lambda: t.info)
        short_pct = info.get("shortPercentOfFloat")
        short_ratio = info.get("shortRatio")

        signal = "moderate"
        if short_pct and short_pct > 0.20:
            signal = "elevated"
        elif short_pct and short_pct < 0.05:
            signal = "low"

        return ShortInterest(
            symbol=symbol.upper(),
            short_float_pct=round(short_pct * 100, 2) if short_pct else None,
            days_to_cover=round(short_ratio, 1) if short_ratio else None,
            signal=signal,
        )
    except Exception as e:
        logger.warning(f"Failed to fetch short interest for {symbol}: {e}")
        return None


async def get_options_flow_signals(
    symbol: str,
    config: AlphaPulseConfig | None = None,
) -> list[OptionsFlowSignal]:
    """Detect unusual options activity.

    Phase 1: Basic put/call volume from Yahoo Finance options chain.
    Future phases will scrape Market Chameleon / Barchart for more detail.
    """
    signals = []
    try:
        t = await asyncio.to_thread(lambda: yf.Ticker(symbol))

        for exp_date_str in (await asyncio.to_thread(lambda: t.options))[:3]:
            try:
                chain = await asyncio.to_thread(lambda d=exp_date_str: t.option_chain(d))
                calls = chain.calls
                puts = chain.puts

                total_call_vol = calls["volume"].sum() if "volume" in calls.columns else 0
                total_put_vol = puts["volume"].sum() if "volume" in puts.columns else 0
                total_call_oi = calls["openInterest"].sum() if "openInterest" in calls.columns else 0
                total_put_oi = puts["openInterest"].sum() if "openInterest" in puts.columns else 0

                if total_call_vol > total_call_oi * 0.5 and total_call_oi > 0:
                    signals.append(OptionsFlowSignal(
                        symbol=symbol.upper(),
                        type="unusual_call",
                        contracts=int(total_call_vol),
                        description=f"Elevated call volume ({int(total_call_vol)} vs OI {int(total_call_oi)}) at {exp_date_str}",
                    ))

                if total_put_vol > total_put_oi * 0.5 and total_put_oi > 0:
                    signals.append(OptionsFlowSignal(
                        symbol=symbol.upper(),
                        type="unusual_put",
                        contracts=int(total_put_vol),
                        description=f"Elevated put volume ({int(total_put_vol)} vs OI {int(total_put_oi)}) at {exp_date_str}",
                    ))
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"Failed to analyze options flow for {symbol}: {e}")

    return signals[:5]
