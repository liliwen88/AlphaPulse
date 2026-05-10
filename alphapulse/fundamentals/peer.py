from __future__ import annotations

import asyncio
import logging

import yfinance as yf

from alphapulse.core.config import AlphaPulseConfig
from alphapulse.fundamentals.models import PeerComparison, PeerMetric

logger = logging.getLogger(__name__)


async def find_peers(
    symbol: str,
    num_peers: int = 5,
    config: AlphaPulseConfig | None = None,
) -> PeerComparison:
    """Find peer companies using sector/industry data from Yahoo Finance."""
    symbol = symbol.strip().upper()
    try:
        t = await asyncio.to_thread(lambda: yf.Ticker(symbol))
        info = await asyncio.to_thread(lambda: t.info)
        sector = info.get("sector", "")
        industry = info.get("industry", "")

        if not sector and not industry:
            return PeerComparison(primary_symbol=symbol, peers=[])

        peer_symbols = _get_peer_symbols(symbol, sector, industry, num_peers * 2)

        peers = []
        for psym in peer_symbols[:num_peers * 2]:
            if len(peers) >= num_peers:
                break
            try:
                pt = await asyncio.to_thread(lambda s=psym: yf.Ticker(s))
                pinfo = await asyncio.to_thread(lambda x=pt: x.info)()
                if not pinfo or pinfo.get("symbol") is None:
                    continue
                peer = PeerMetric(
                    symbol=psym,
                    company_name=pinfo.get("shortName") or pinfo.get("longName") or psym,
                    market_cap_billions=(
                        round(pinfo.get("marketCap", 0) / 1e9, 2)
                        if pinfo.get("marketCap")
                        else None
                    ),
                    pe_ratio=pinfo.get("trailingPE") or pinfo.get("forwardPE"),
                    ev_ebitda=pinfo.get("enterpriseToEbitda"),
                    revenue_growth_pct=(
                        round(pinfo["revenueGrowth"] * 100, 1)
                        if pinfo.get("revenueGrowth")
                        else None
                    ),
                    net_margin_pct=(
                        round(pinfo["profitMargins"] * 100, 1)
                        if pinfo.get("profitMargins")
                        else None
                    ),
                )
                peers.append(peer)
            except Exception as e:
                logger.debug(f"Failed to fetch peer {psym}: {e}")

        return PeerComparison(primary_symbol=symbol, peers=peers)
    except Exception as e:
        logger.warning(f"Failed to find peers for {symbol}: {e}")
        return PeerComparison(primary_symbol=symbol, peers=[])


def _get_peer_symbols(symbol: str, sector: str, industry: str, count: int) -> list[str]:
    """Map sector/industry to known peer groups."""
    sector_peers = {
        "Technology": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "ADBE", "CRM",
            "ORCL", "CSCO", "INTC", "AMD", "QCOM", "TXN", "AVGO", "IBM",
        ],
        "Financial Services": [
            "JPM", "BAC", "WFC", "C", "GS", "MS", "SCHW", "BLK",
            "V", "MA", "AXP", "PYPL", "SQ",
        ],
        "Healthcare": [
            "UNH", "JNJ", "PFE", "ABBV", "MRK", "LLY", "ABT", "TMO",
            "DHR", "BMY", "GILD", "AMGN", "ISRG", "VRTX", "REGN",
        ],
        "Consumer Cyclical": [
            "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW",
            "BKNG", "MAR", "TJX", "LULU",
        ],
        "Consumer Defensive": [
            "WMT", "PG", "KO", "PEP", "COST", "PM", "MO", "CL",
            "KMB", "GIS",
        ],
        "Energy": [
            "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO",
            "OXY", "DVN", "HAL",
        ],
        "Industrials": [
            "BA", "CAT", "GE", "HON", "UNP", "UPS", "LMT", "RTX",
            "DE", "MMM", "EMR", "FDX",
        ],
        "Communication Services": [
            "GOOGL", "META", "NFLX", "DIS", "VZ", "T", "TMUS", "CMCSA",
            "CHTR", "SPOT",
        ],
        "Real Estate": [
            "PLD", "AMT", "CCI", "EQIX", "SPG", "PSA", "O", "WELL", "AVB",
        ],
        "Utilities": [
            "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "PCG",
        ],
        "Basic Materials": [
            "LIN", "APD", "SHW", "FCX", "NEM", "DOW", "DD", "ECL",
            "GOLD", "NUE",
        ],
    }

    all_peers = sector_peers.get(sector, [])
    return [s for s in all_peers if s != symbol][:count]
